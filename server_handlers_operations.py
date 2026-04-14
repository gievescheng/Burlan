from __future__ import annotations

import tempfile
import traceback
from pathlib import Path

from flask import jsonify, request, send_file

import ops_data


def api_calibration_records_list():
    return jsonify({'items': ops_data.load_records('calibration')})


def api_calibration_records_save(json_body, json_error, load_burlan_calibration_instruments):
    try:
        body = json_body()
        record = body.get('record') or body
        if not isinstance(record, dict):
            return json_error('校正更新資料格式不正確。')
        instrument_id = str(record.get('instrumentId') or '').strip()
        calibration_date = str(record.get('calibrationDate') or '').strip()
        if not instrument_id:
            return json_error('請提供儀器編號。')
        if not calibration_date:
            return json_error('請提供本次校正日期。')
        _items, saved = ops_data.upsert_records('calibration', [record])
        payload = load_burlan_calibration_instruments()
        payload['saved'] = saved
        return jsonify(payload)
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_training_records_list():
    return jsonify({'items': ops_data.load_records('training')})


def api_training_records_save(save_ops_records, json_error):
    try:
        return save_ops_records('training')
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_training_records_delete(record_id, json_error):
    try:
        items, deleted = ops_data.delete_record('training', record_id)
        if not deleted:
            return json_error('Record not found.', 404)
        return jsonify({'items': items, 'deleted_id': record_id})
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_equipment_records_list(load_burlan_equipment_records):
    return jsonify(load_burlan_equipment_records())


def api_equipment_records_save(json_body, json_error, load_burlan_equipment_records):
    try:
        body = json_body()
        records = body.get('records')
        if records is None:
            record = body.get('record')
            records = record if isinstance(record, list) else [record or body]
        if not isinstance(records, list) or not records:
            return json_error('No records provided.')
        _items, saved = ops_data.upsert_records(
            'equipment',
            [record for record in records if isinstance(record, dict)],
        )
        payload = load_burlan_equipment_records()
        payload['saved'] = saved
        return jsonify(payload)
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_equipment_records_delete(record_id, json_error, load_burlan_equipment_records):
    try:
        _items, deleted = ops_data.delete_record('equipment', record_id)
        if not deleted:
            return json_error('找不到可刪除的系統資料；柏連原始來源資料不可直接刪除。', 404)
        payload = load_burlan_equipment_records()
        payload['deleted_id'] = record_id
        return jsonify(payload)
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_supplier_records_list(load_burlan_supplier_records):
    return jsonify(load_burlan_supplier_records())


def api_supplier_records_save(json_body, json_error, load_burlan_supplier_records):
    try:
        body = json_body()
        records = body.get('records')
        if records is None:
            record = body.get('record')
            records = record if isinstance(record, list) else [record or body]
        if not isinstance(records, list) or not records:
            return json_error('No records provided.')
        _items, saved = ops_data.upsert_records(
            'supplier',
            [record for record in records if isinstance(record, dict)],
        )
        payload = load_burlan_supplier_records()
        payload['saved'] = saved
        return jsonify(payload)
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_supplier_records_delete(record_id, json_error, load_burlan_supplier_records):
    try:
        _items, deleted = ops_data.delete_record('supplier', record_id)
        if not deleted:
            return json_error('找不到可刪除的系統資料；柏連原始來源資料不可直接刪除。', 404)
        payload = load_burlan_supplier_records()
        payload['deleted_id'] = record_id
        return jsonify(payload)
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_nonconformances_list(enrich_audit_plans_with_nonconformance_summary):
    return jsonify({
        'items': ops_data.load_records('nonconformance'),
        'audit_plans': enrich_audit_plans_with_nonconformance_summary(),
    })


def api_nonconformances_save(json_body, json_error, enrich_audit_plans_with_nonconformance_summary):
    try:
        body = json_body()
        records = body.get('records')
        if records is None:
            record = body.get('record')
            records = record if isinstance(record, list) else [record or body]
        if not isinstance(records, list) or not records:
            return json_error('No records provided.')
        items, saved = ops_data.upsert_records(
            'nonconformance',
            [record for record in records if isinstance(record, dict)],
        )
        return jsonify({
            'items': items,
            'saved': saved,
            'audit_plans': enrich_audit_plans_with_nonconformance_summary(),
        })
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_nonconformances_delete(record_id, json_error, enrich_audit_plans_with_nonconformance_summary):
    try:
        items, deleted = ops_data.delete_record('nonconformance', record_id)
        if not deleted:
            return json_error('Record not found.', 404)
        return jsonify({
            'items': items,
            'deleted_id': record_id,
            'audit_plans': enrich_audit_plans_with_nonconformance_summary(),
        })
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_nonconformances_import(json_error):
    try:
        upload = request.files.get('file')
        if upload is None or not upload.filename:
            return json_error('Upload file is required.')
        return jsonify(ops_data.parse_import('nonconformance', upload))
    except ValueError as exc:
        return json_error(str(exc), 400)
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_audit_plans_list(load_burlan_audit_plans, enrich_audit_plans_with_nonconformance_summary):
    payload = load_burlan_audit_plans()
    payload['items'] = enrich_audit_plans_with_nonconformance_summary(payload.get('items', []))
    return jsonify(payload)


def api_audit_plans_save(json_body, json_error, load_burlan_audit_plans, enrich_audit_plans_with_nonconformance_summary):
    try:
        body = json_body()
        records = body.get('records')
        if records is None:
            record = body.get('record')
            records = record if isinstance(record, list) else [record or body]
        if not isinstance(records, list) or not records:
            return json_error('No records provided.')
        _items, saved = ops_data.upsert_records(
            'auditplan',
            [record for record in records if isinstance(record, dict)],
        )
        payload = load_burlan_audit_plans()
        payload['items'] = enrich_audit_plans_with_nonconformance_summary(payload.get('items', []))
        payload['saved'] = saved
        return jsonify(payload)
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_audit_plans_delete(record_id, json_error, load_burlan_audit_plans, enrich_audit_plans_with_nonconformance_summary):
    try:
        source_ids = {
            str(item.get('id') or '').strip()
            for item in load_burlan_audit_plans().get('items', [])
            if item.get('source_system') == 'burlan_audit_plan'
        }
        if record_id in source_ids:
            return json_error('柏連原始年度稽核計畫不可直接刪除，請修改原始程序文件。', 404)
        _items, deleted = ops_data.delete_record('auditplan', record_id)
        if not deleted:
            return json_error('Record not found.', 404)
        payload = load_burlan_audit_plans()
        payload['items'] = enrich_audit_plans_with_nonconformance_summary(payload.get('items', []))
        payload['deleted_id'] = record_id
        return jsonify(payload)
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_audit_plans_import(json_error):
    try:
        upload = request.files.get('file')
        if upload is None or not upload.filename:
            return json_error('Upload file is required.')
        return jsonify(ops_data.parse_import('auditplan', upload))
    except ValueError as exc:
        return json_error(str(exc), 400)
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_audit_plan_attachments(record_id, json_error, load_burlan_audit_plans):
    try:
        items = load_burlan_audit_plans().get('items', [])
        return jsonify({'attachments': ops_data.list_auditplan_attachments(record_id, items)})
    except KeyError:
        return json_error('Record not found.', 404)
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_audit_plan_year_bundle(json_error, build_audit_plan_year_bundle):
    try:
        year = str(request.args.get('year') or '').strip()
        if not year:
            return json_error('請先指定要下載的年度。')
        out_stream, download_name = build_audit_plan_year_bundle(year)
        return send_file(
            out_stream,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/zip',
        )
    except ValueError as exc:
        return json_error(str(exc), 404)
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_environment_records_list():
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    items = ops_data.filter_environment_records(start, end)
    return jsonify({'items': items, 'summary': ops_data.summarize_environment(items)})


def api_environment_records_save(save_ops_records, json_error):
    try:
        return save_ops_records('environment')
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_environment_records_delete(record_id, json_error):
    try:
        items, deleted = ops_data.delete_record('environment', record_id)
        if not deleted:
            return json_error('Record not found.', 404)
        return jsonify({
            'items': items,
            'summary': ops_data.summarize_environment(items),
            'deleted_id': record_id,
        })
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_environment_records_import(json_error):
    try:
        upload = request.files.get('file')
        if upload is None or not upload.filename:
            return json_error('Upload file is required.')
        return jsonify(ops_data.parse_import('environment', upload))
    except ValueError as exc:
        return json_error(str(exc), 400)
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_environment_records_delete_range(json_body, json_error):
    try:
        body = json_body()
        start = body.get('start', '')
        end = body.get('end', '')
        items, removed = ops_data.delete_environment_range(start, end)
        return jsonify({
            'items': items,
            'summary': ops_data.summarize_environment(items),
            'removed_count': removed,
            'deleted': removed,
        })
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_production_records_read_existing(json_error):
    try:
        import record_imports

        records, source_file = record_imports.load_existing_production_records()
        return jsonify({'records': records, 'source_file': source_file})
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_production_records_import(json_error):
    temp_path = None
    try:
        import record_imports

        uploaded = request.files.get('file')
        if not uploaded or not uploaded.filename:
            return json_error('請先選擇生產日報 Excel 檔案。', 400)

        suffix = Path(uploaded.filename).suffix or '.xlsx'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            uploaded.save(tmp.name)
            temp_path = Path(tmp.name)

        records, _ = record_imports.load_uploaded_production_records(temp_path)
        if not records:
            return json_error('這份檔案沒有讀到可辨識的生產日報資料，請確認是否為正式生產日報格式。', 400)
        return jsonify({'records': records, 'source_file': uploaded.filename})
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)


def api_quality_records_read_existing(json_error):
    try:
        import record_imports

        records, source_file = record_imports.load_existing_quality_records()
        return jsonify({'records': records, 'source_file': source_file})
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)


def api_quality_records_import(json_error):
    temp_path = None
    try:
        import record_imports

        uploaded = request.files.get('file')
        if not uploaded or not uploaded.filename:
            return json_error('請先選擇品質檢驗 Excel 檔案。', 400)

        suffix = Path(uploaded.filename).suffix or '.xlsx'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            uploaded.save(tmp.name)
            temp_path = Path(tmp.name)

        records, _ = record_imports.load_uploaded_quality_records(temp_path)
        if not records:
            return json_error('這份檔案沒有讀到可辨識的品質檢驗資料，請確認是否為正式品質記錄格式。', 400)
        return jsonify({'records': records, 'source_file': uploaded.filename})
    except Exception as exc:
        traceback.print_exc()
        return json_error(str(exc), 500)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)


def api_generate(json_error):
    try:
        import generate_record

        body = request.get_json(force=True)
        rec_type = body.get('type', '')
        data = body.get('data', [])

        if rec_type not in ('env', 'production', 'quality'):
            return jsonify({'error': f'Unsupported type: {rec_type}'}), 400

        tmp = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False, dir=tempfile.gettempdir())
        tmp.close()
        out_path = generate_record.run(rec_type, data, tmp.name)

        filenames = {
            'env': '環境監測記錄.xlsx',
            'production': '生產記錄.xlsx',
            'quality': '品質檢驗記錄.xlsx',
        }
        return send_file(
            out_path,
            as_attachment=True,
            download_name=filenames[rec_type],
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
    except Exception as exc:
        traceback.print_exc()
        return jsonify({'error': str(exc)}), 500


def api_record_engine_catalog():
    try:
        import record_engine

        return jsonify({'templates': record_engine.get_catalog()})
    except Exception as exc:
        traceback.print_exc()
        return jsonify({'error': str(exc)}), 500


def api_record_engine_suggest():
    try:
        import record_engine

        body = request.get_json(force=True) or {}
        prompt = body.get('prompt', '')
        context = body.get('context') or {}
        return jsonify({'templates': record_engine.suggest_templates(prompt, context)})
    except Exception as exc:
        traceback.print_exc()
        return jsonify({'error': str(exc)}), 500


def api_record_engine_precheck():
    try:
        import record_engine

        body = request.get_json(force=True) or {}
        return jsonify({'result': record_engine.precheck_template(body)})
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:
        traceback.print_exc()
        return jsonify({'error': str(exc)}), 500


def api_record_engine_generate():
    try:
        import record_engine

        body = request.get_json(force=True) or {}
        out_path, download_name, mimetype = record_engine.generate_template(body)
        return send_file(
            str(out_path),
            as_attachment=True,
            download_name=download_name,
            mimetype=mimetype,
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:
        traceback.print_exc()
        return jsonify({'error': str(exc)}), 500


def shipment_draft_catalog():
    try:
        import shipment_draft

        return jsonify({'orders': shipment_draft.get_order_catalog()})
    except Exception as exc:
        traceback.print_exc()
        return jsonify({'error': str(exc)}), 500


def shipment_draft_generate():
    try:
        import shipment_draft

        body = request.get_json(force=True) or {}
        out_path, download_name = shipment_draft.build_shipment_draft(body)
        return send_file(
            out_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:
        traceback.print_exc()
        return jsonify({'error': str(exc)}), 500
