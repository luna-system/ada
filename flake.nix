{
  description = "Ada - Privacy-first conversational AI with RAG";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        # Use python313 if available, fallback to python312 or python3
        python = pkgs.python313 or pkgs.python312 or pkgs.python3;
        
        # Python environment with all Ada dependencies
        adaPythonEnv = python.withPackages (ps: with ps; [
          # Core dependencies
          click
          fastapi
          uvicorn
          gunicorn
          httpx
          requests
          
          # Configuration
          pydantic
          pydantic-settings
          python-dotenv
          
          # RAG / vector store
          chromadb
          
          # Cloud storage (Backblaze R2)
          boto3
          
          # OCR and file upload
          python-multipart
          pytesseract
          pillow
          
          # Development
          pytest
          pytest-asyncio
          
          # Documentation
          sphinx
          sphinx-rtd-theme
        ]);

      in
      {
        # Development shell: `nix develop`
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python environment with Ada dependencies
            adaPythonEnv
            
            # System dependencies
            tesseract  # OCR support
            pkg-config
            gcc
            
            # Optional but recommended
            ollama  # LLM runtime
            git
            curl
            jq
            
            # Development tools
            uv  # Fast Python package manager
            ruff  # Python linter/formatter
          ];

          shellHook = ''
            echo "🤖 Ada development environment"
            echo ""
            echo "Available commands:"
            echo "  ada          - Master CLI tool"
            echo "  ollama       - LLM runtime"
            echo "  python       - Python ${python.version}"
            echo "  pytest       - Run tests"
            echo ""
            echo "Quick start:"
            echo "  1. ollama serve &  # Start Ollama (or use existing)"
            echo "  2. ollama pull deepseek-r1:latest  # Pull model"
            echo "  3. cp .env.example .env  # Configure"
            echo "  4. ada setup  # Initialize Ada"
            echo "  5. ada run    # Start Ada"
            echo ""
            
            # Set up local data directory
            export DATA_DIR="''${DATA_DIR:-./data}"
            export CHROMA_MODE="embedded"
            
            # Use local Ollama by default
            export OLLAMA_BASE_URL="''${OLLAMA_BASE_URL:-http://localhost:11434}"
            
            # Add current directory to PYTHONPATH for development
            export PYTHONPATH="$PWD:$PYTHONPATH"
            
            # Create data directory if it doesn't exist
            mkdir -p "$DATA_DIR"
            
            echo "Environment configured for local mode."
            echo "Data directory: $DATA_DIR"
            echo "Ollama URL: $OLLAMA_BASE_URL"
            echo ""
          '';
        };

        # Ada package: `nix build`
        packages.default = python.pkgs.buildPythonApplication {
          pname = "ada-v1";
          version = "1.6.0";
          
          src = ./.;
          
          format = "pyproject";
          
          nativeBuildInputs = with python.pkgs; [
            setuptools
          ];
          
          propagatedBuildInputs = with python.pkgs; [
            click
            fastapi
            uvicorn
            gunicorn
            httpx
            requests
            pydantic
            pydantic-settings
            python-dotenv
            chromadb
            boto3
            python-multipart
            pytesseract
            pillow
          ];
          
          # Runtime dependencies
          buildInputs = with pkgs; [
            tesseract
          ];
          
          # Don't run tests during build (they need Ollama)
          doCheck = false;
          
          meta = with pkgs.lib; {
            description = "Privacy-first conversational AI with RAG";
            homepage = "https://github.com/luna-system/ada";
            license = licenses.unlicense;
            maintainers = [ ];
          };
        };

        # Run Ada directly: `nix run`
        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/ada";
        };
        
        # Additional apps for convenience
        apps.ada = self.apps.${system}.default;
        
        apps.ada-setup = {
          type = "app";
          program = pkgs.writeShellScript "ada-setup" ''
            ${self.packages.${system}.default}/bin/ada setup
          '';
        };
        
        apps.ada-doctor = {
          type = "app";
          program = pkgs.writeShellScript "ada-doctor" ''
            ${self.packages.${system}.default}/bin/ada doctor
          '';
        };
      }
    ) // {
      # NixOS module for system-wide installation
      nixosModules.default = { config, lib, pkgs, ... }:
        with lib;
        let
          cfg = config.services.ada;
        in {
          options.services.ada = {
            enable = mkEnableOption "Ada conversational AI service";
            
            package = mkOption {
              type = types.package;
              default = self.packages.${pkgs.system}.default;
              description = "Ada package to use";
            };
            
            dataDir = mkOption {
              type = types.path;
              default = "/var/lib/ada";
              description = "Data directory for Ada";
            };
            
            ollamaUrl = mkOption {
              type = types.str;
              default = "http://localhost:11434";
              description = "Ollama API endpoint";
            };
            
            port = mkOption {
              type = types.port;
              default = 8000;
              description = "Port for Ada API";
            };
            
            user = mkOption {
              type = types.str;
              default = "ada";
              description = "User to run Ada as";
            };
            
            group = mkOption {
              type = types.str;
              default = "ada";
              description = "Group to run Ada as";
            };
          };
          
          config = mkIf cfg.enable {
            users.users.${cfg.user} = {
              isSystemUser = true;
              group = cfg.group;
              home = cfg.dataDir;
              createHome = true;
              description = "Ada AI service user";
            };
            
            users.groups.${cfg.group} = {};
            
            systemd.services.ada = {
              description = "Ada conversational AI service";
              after = [ "network.target" ];
              wantedBy = [ "multi-user.target" ];
              
              environment = {
                DATA_DIR = cfg.dataDir;
                OLLAMA_BASE_URL = cfg.ollamaUrl;
                CHROMA_MODE = "embedded";
                PORT = toString cfg.port;
              };
              
              serviceConfig = {
                Type = "simple";
                User = cfg.user;
                Group = cfg.group;
                WorkingDirectory = cfg.dataDir;
                ExecStart = "${cfg.package}/bin/ada run --host 0.0.0.0 --port ${toString cfg.port}";
                Restart = "on-failure";
                RestartSec = "10s";
                
                # Security hardening
                NoNewPrivileges = true;
                PrivateTmp = true;
                ProtectSystem = "strict";
                ProtectHome = true;
                ReadWritePaths = [ cfg.dataDir ];
              };
            };
            
            # Optionally enable Ollama service
            services.ollama.enable = mkDefault true;
          };
        };
    };
}
