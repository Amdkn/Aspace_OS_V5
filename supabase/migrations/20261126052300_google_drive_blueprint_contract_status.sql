BEGIN;

UPDATE integration.provider_adapter_blueprints
SET auth_contract_status='SPECIFIED',
    supported_operations=ARRAY[
      'health_check','list_files','get_file','create_folder',
      'update_file_metadata','delete_file'
    ]::text[]
WHERE provider_key='files-knowledge-google-drive'
  AND implementation_status='PLANNED';

DO $verify$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM integration.provider_adapter_blueprints
    WHERE provider_key='files-knowledge-google-drive'
      AND implementation_status='PLANNED'
      AND auth_contract_status='SPECIFIED'
      AND supported_operations @> ARRAY[
        'health_check','list_files','get_file','create_folder',
        'update_file_metadata','delete_file'
      ]::text[]
  ) THEN
    RAISE EXCEPTION 'Google Drive blueprint contract update failed';
  END IF;
END
$verify$;

COMMIT;
