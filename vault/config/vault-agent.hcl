vault {
  address      = "https://vault:8200"
  ca_cert_file = "/vault/tls/ca.crt"
}

auto_auth {
  method "approle" {
    mount_path = "auth/approle"

    config = {
      role_id_file_path   = "/vault/agent/role_id"
      secret_id_file_path = "/vault/agent/secret_id"

      remove_secret_id_file_after_reading = false
    }
  }

  sink "file" {
    config = {
      path = "/vault/agent/token"
      mode = 0640
    }
  }
}
