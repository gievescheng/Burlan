from __future__ import annotations

import traceback
from urllib.parse import urlencode

import requests
from flask import jsonify, redirect, request, session


def google_status_payload(
    load_google_config,
    load_google_tokens,
    google_configured,
    google_redirect_uri,
):
    config = load_google_config()
    tokens = load_google_tokens()
    return {
        'configured': google_configured(config),
        'connected': bool(tokens.get('access_token')),
        'email': tokens.get('email', ''),
        'name': tokens.get('name', ''),
        'redirect_uri': google_redirect_uri(),
        'has_refresh_token': bool(tokens.get('refresh_token')),
        'expires_at': tokens.get('expires_at'),
    }


def build_event_payload(item: dict, add_days) -> dict:
    date_value = str(item.get('date', '')).strip()
    if len(date_value) != 10:
        raise ValueError('Each alert item must include a YYYY-MM-DD date.')

    title = str(item.get('title') or 'Audit reminder').strip()
    module = str(item.get('module') or '').strip()
    summary = str(item.get('summary') or '').strip()
    owner = str(item.get('owner') or '').strip()

    details = [
        f'Module: {module}' if module else '',
        f'Summary: {summary}' if summary else '',
        f'Owner: {owner}' if owner else '',
    ]
    return {
        'summary': title,
        'description': '\n'.join(line for line in details if line),
        'start': {'date': date_value},
        'end': {'date': add_days(date_value, 1)},
    }


def api_notion():
    try:
        body = request.get_json(force=True)
        token = body.get('token', '').strip()
        db_id = body.get('db_id', '').strip()
        properties = body.get('properties', {})

        if not token or not db_id:
            return jsonify({'error': 'token and db_id are required.'}), 400

        response = requests.post(
            'https://api.notion.com/v1/pages',
            json={'parent': {'database_id': db_id}, 'properties': properties},
            headers={
                'Authorization': f'Bearer {token}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json',
            },
            timeout=20,
        )
        return jsonify(response.json()), response.status_code
    except Exception as exc:
        traceback.print_exc()
        return jsonify({'error': str(exc)}), 500


def google_calendar_status(google_status_payload_fn):
    return jsonify(google_status_payload_fn())


def google_calendar_config(
    save_google_config,
    clear_google_config,
    clear_google_tokens,
    google_status_payload_fn,
):
    body = request.get_json(force=True) or {}
    if body.get('clear'):
        clear_google_config()
        clear_google_tokens()
        return jsonify(google_status_payload_fn())

    client_id = body.get('client_id', '').strip()
    client_secret = body.get('client_secret', '').strip()
    if not client_id or not client_secret:
        return jsonify({'error': 'client_id and client_secret are required.'}), 400

    save_google_config(client_id, client_secret)
    clear_google_tokens()
    return jsonify(google_status_payload_fn())


def google_calendar_auth_start(
    load_google_config,
    google_configured,
    google_redirect_uri,
    google_auth_url,
    google_scopes,
    token_urlsafe,
):
    config = load_google_config()
    if not google_configured(config):
        return jsonify({'error': 'Google Calendar is not configured yet.'}), 400

    state = token_urlsafe(24)
    session['google_oauth_state'] = state
    auth_url = google_auth_url + '?' + urlencode({
        'client_id': config['client_id'],
        'redirect_uri': google_redirect_uri(),
        'response_type': 'code',
        'scope': ' '.join(google_scopes),
        'access_type': 'offline',
        'prompt': 'consent',
        'include_granted_scopes': 'true',
        'state': state,
    })
    return jsonify({'auth_url': auth_url, 'redirect_uri': google_redirect_uri()})


def google_calendar_oauth_callback(load_google_config, exchange_google_code, save_google_tokens):
    expected_state = session.get('google_oauth_state')
    incoming_state = request.args.get('state', '')
    if not expected_state or expected_state != incoming_state:
        return redirect('/?google=error&reason=state')

    if request.args.get('error'):
        return redirect('/?google=error&reason=' + request.args.get('error', 'oauth'))

    code = request.args.get('code', '')
    if not code:
        return redirect('/?google=error&reason=missing_code')

    try:
        config = load_google_config()
        tokens = exchange_google_code(code, config)
        save_google_tokens(tokens)
        session.pop('google_oauth_state', None)
        return redirect('/?google=connected')
    except Exception:
        traceback.print_exc()
        return redirect('/?google=error&reason=token_exchange')


def google_calendar_events(
    require_google_access_token,
    google_error_text,
    build_event_payload_fn,
    google_calendar_events_url,
):
    try:
        body = request.get_json(force=True) or {}
        items = body.get('items')
        if items is None:
            items = [body]
        if not isinstance(items, list) or not items:
            return jsonify({'error': 'items must be a non-empty array.'}), 400

        access_token, tokens = require_google_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        results = []
        success_count = 0
        for item in items:
            try:
                payload = build_event_payload_fn(item)
                response = requests.post(
                    google_calendar_events_url,
                    json=payload,
                    headers=headers,
                    timeout=20,
                )
                if not response.ok:
                    raise RuntimeError(google_error_text(response))
                event = response.json()
                results.append({
                    'title': item.get('title', ''),
                    'success': True,
                    'event_id': event.get('id', ''),
                    'html_link': event.get('htmlLink', ''),
                })
                success_count += 1
            except Exception as exc:
                results.append({
                    'title': item.get('title', ''),
                    'success': False,
                    'error': str(exc),
                })

        failed_count = len(results) - success_count
        status_code = 200 if failed_count == 0 else 207
        return jsonify({
            'email': tokens.get('email', ''),
            'success_count': success_count,
            'failed_count': failed_count,
            'results': results,
        }), status_code
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:
        traceback.print_exc()
        return jsonify({'error': str(exc)}), 500


def google_calendar_logout(clear_google_tokens, google_status_payload_fn):
    clear_google_tokens()
    return jsonify(google_status_payload_fn())
