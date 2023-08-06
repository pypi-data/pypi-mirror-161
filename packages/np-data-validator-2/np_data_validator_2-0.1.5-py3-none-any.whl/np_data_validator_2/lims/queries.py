EXP_QUERY = """
SELECT es.id AS es_id, 
    es.name AS es,
    es.storage_directory,
    es.workflow_state,
    es.date_of_acquisition,
    es.stimulus_name,
    es.foraging_id as foraging_id,
    sp.external_specimen_name,
    isi.id AS isi_experiment_id,
    e.name AS rig,
    u.login AS operator,
    p.code AS project,
    wkft.name AS wkft, 
    wkf.storage_directory || wkf.filename AS wkf_path,
    bs.storage_directory AS behavior_dir
FROM ecephys_sessions es
    JOIN specimens sp ON sp.id = es.specimen_id
    LEFT JOIN isi_experiments isi ON isi.id = es.isi_experiment_id
    LEFT JOIN equipment e ON e.id = es.equipment_id
    LEFT JOIN users u ON u.id = es.operator_id
    JOIN projects p ON p.id = es.project_id
    LEFT JOIN well_known_files wkf ON wkf.attachable_id = es.id
    LEFT JOIN well_known_file_types wkft ON wkft.id=wkf.well_known_file_type_id
    LEFT JOIN behavior_sessions bs ON bs.foraging_id = es.foraging_id
WHERE es.id = {}
ORDER BY es.id
"""

IMAGE_QUERY = """
SELECT es.id AS es_id, es.name AS es, imt.name AS image_type, es.storage_directory || im.jp2 AS image_path
FROM ecephys_sessions es
    JOIN observatory_associated_data oad ON oad.observatory_record_id = es.id AND oad.observatory_record_type = 'EcephysSession'
    JOIN images im ON im.id=oad.observatory_file_id AND oad.observatory_file_type = 'Image'
    JOIN image_types imt ON imt.id=im.image_type_id
WHERE es.id = {}
ORDER BY es.id, imt.name;
"""

PROBE_QUERY = """
SELECT es.id AS es_id, 
    es.name AS es, 
    ep.name AS ep, 
    ep.id AS ep_id, 
    wkft.name AS wkft, 
    wkf.storage_directory || wkf.filename AS wkf_path
FROM ecephys_sessions es
    JOIN ecephys_probes ep ON ep.ecephys_session_id=es.id
    LEFT JOIN well_known_files wkf ON wkf.attachable_id = ep.id
    LEFT JOIN well_known_file_types wkft ON wkft.id=wkf.well_known_file_type_id
WHERE es.id = {} 
ORDER BY es.id, ep.name;
"""
