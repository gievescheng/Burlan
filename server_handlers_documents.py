from __future__ import annotations

from flask import Response, jsonify, request

import ops_data


def api_view_file(serve_managed_file):
    return serve_managed_file(request.args.get('path', ''), False)


def api_download_file(serve_managed_file):
    return serve_managed_file(request.args.get('path', ''), True)


def api_preview_text_file():
    html_payload = ops_data.build_text_preview_html(request.args.get('path', ''))
    if html_payload is None:
        return Response('找不到可預覽的文字內容。', status=404, mimetype='text/plain')
    return Response(html_payload, mimetype='text/html')


def api_burlan_master_documents(load_burlan_master_documents):
    return jsonify(load_burlan_master_documents())


def api_burlan_quality_objectives(load_burlan_quality_objectives):
    return jsonify(load_burlan_quality_objectives())


def api_burlan_calibration_instruments(load_burlan_calibration_instruments):
    return jsonify(load_burlan_calibration_instruments())
