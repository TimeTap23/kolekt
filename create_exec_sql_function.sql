-- Create the exec_sql function for executing arbitrary SQL
-- This function allows the service role to execute SQL statements

CREATE OR REPLACE FUNCTION exec_sql(sql text)
RETURNS json AS $$
DECLARE
  result json;
BEGIN
  -- Only allow service role to execute this function
  IF auth.role() != 'service_role' THEN
    RAISE EXCEPTION 'Only service role can execute this function';
  END IF;
  
  -- Execute the SQL and return results as JSON
  EXECUTE 'SELECT json_agg(row_to_json(t)) FROM (' || sql || ') t' INTO result;
  RETURN COALESCE(result, '[]'::json);
EXCEPTION
  WHEN OTHERS THEN
    -- Return error information as JSON
    RETURN json_build_object(
      'error', SQLERRM,
      'detail', SQLSTATE
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission to service role only
GRANT EXECUTE ON FUNCTION exec_sql(text) TO service_role;
REVOKE EXECUTE ON FUNCTION exec_sql(text) FROM authenticated;
REVOKE EXECUTE ON FUNCTION exec_sql(text) FROM anon;
