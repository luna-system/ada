Build System
============

Ada uses Docker BuildKit with BuildX for fast, consistent builds.

Why BuildKit?
-------------

BuildKit provides significant advantages for Ada's multi-service architecture:

- **Better caching**: COPY commands don't invalidate unnecessarily
- **Parallel builds**: Multiple services build simultaneously
- **Consistent behavior**: Same as CI/CD pipelines
- **Modern features**: Multi-stage builds, cache mounts, secrets

Build Performance
-----------------

With BuildKit enabled:

- Initial build: ~5-8 minutes (downloading base images)
- Rebuilds with changes: ~30-90 seconds (cached layers)
- No changes: ~5 seconds (full cache hit)

Without BuildKit:

- Initial build: ~10-15 minutes
- Rebuilds: ~2-5 minutes (poor caching)
- Frequent cache misses

Prerequisites
-------------

Check BuildX Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check if BuildX is available
   docker buildx version
   
   # If installed, you'll see:
   # github.com/docker/buildx v0.18.0 ...

If not installed, run the setup script:

.. code-block:: bash

   ./scripts/setup_buildx.sh

This will:

1. Detect your Linux distribution
2. Suggest the appropriate package manager command
3. Optionally install BuildX automatically
4. Create an optimized builder instance named ``ada-builder``

Manual Installation
~~~~~~~~~~~~~~~~~~~

**Arch Linux:**

.. code-block:: bash

   sudo pacman -S docker-buildx

**Debian/Ubuntu:**

.. code-block:: bash

   sudo apt install docker-buildx-plugin

**Fedora:**

.. code-block:: bash

   sudo dnf install docker-buildx-plugin

**Manual (any Linux):**

.. code-block:: bash

   mkdir -p ~/.docker/cli-plugins/
   
   # For x86_64:
   curl -Lo ~/.docker/cli-plugins/docker-buildx \
     https://github.com/docker/buildx/releases/download/v0.18.0/buildx-v0.18.0.linux-amd64
   
   # For ARM64:
   curl -Lo ~/.docker/cli-plugins/docker-buildx \
     https://github.com/docker/buildx/releases/download/v0.18.0/buildx-v0.18.0.linux-arm64
   
   chmod +x ~/.docker/cli-plugins/docker-buildx

Create Builder Instance
~~~~~~~~~~~~~~~~~~~~~~~

After installing BuildX, create Ada's builder:

.. code-block:: bash

   docker buildx create --name ada-builder --use --bootstrap
   
   # Verify
   docker buildx ls

You should see ``ada-builder`` marked with an asterisk (active).

Building Ada
------------

Basic Build
~~~~~~~~~~~

.. code-block:: bash

   # Build all services
   docker compose build
   
   # Build specific service
   docker compose build brain
   docker compose build matrix-bridge

The ``compose.yaml`` is pre-configured to use BuildKit with optimized settings.

Force Rebuild
~~~~~~~~~~~~~

.. code-block:: bash

   # Rebuild without cache
   docker compose build --no-cache
   
   # Rebuild specific service
   docker compose build --no-cache brain

Pull Latest Base Images
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Update base images before building
   docker compose build --pull

Build Configuration
-------------------

Cache Configuration
~~~~~~~~~~~~~~~~~~~

Ada uses local cache storage for BuildKit:

.. code-block:: yaml

   # In compose.yaml
   x-build-config: &build-config
     platforms:
       - linux/amd64
     cache_from:
       - type=local,src=/tmp/.buildx-cache
     cache_to:
       - type=local,dest=/tmp/.buildx-cache

Cache is stored in ``/tmp/.buildx-cache`` (survives reboots on most systems).

.dockerignore Files
~~~~~~~~~~~~~~~~~~~

Each service has a ``.dockerignore`` to reduce build context:

- ``brain/.dockerignore`` - Excludes tests, docs, __pycache__
- ``frontend/.dockerignore`` - Excludes node_modules, dist
- ``matrix-bridge/.dockerignore`` - Excludes tests, venv
- ``scripts/.dockerignore`` - Excludes docs

This significantly speeds up COPY operations.

Troubleshooting
---------------

Warning: "buildx isn't installed"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:**

.. code-block:: text

   WARN[0000] Docker Compose is configured to build using Bake, 
   but buildx isn't installed

**Solution:**

Run the setup script:

.. code-block:: bash

   ./scripts/setup_buildx.sh

Or manually install (see "Manual Installation" above).

Build Using Wrong Files
~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:**

Code changes aren't appearing in container after rebuild.

**Cause:**

BuildKit cached the COPY layer even though files changed.

**Solution:**

.. code-block:: bash

   # Force rebuild
   docker compose build --no-cache <service>
   
   # Or touch files to update timestamps
   touch matrix-bridge/*.py
   docker compose build matrix-bridge

"permission denied" Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:**

.. code-block:: text

   ERROR: failed to solve: failed to compute cache key: 
   failed to stat /home/luna/Code/ada-v1/data: permission denied

**Cause:**

Docker doesn't have permission to access files.

**Solution:**

Check file permissions and add to docker group:

.. code-block:: bash

   # Add yourself to docker group
   sudo usermod -aG docker $USER
   
   # Log out and back in for changes to take effect

"no space left on device"
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:**

Build fails with disk space error.

**Solution:**

.. code-block:: bash

   # Clean up Docker
   docker system prune -af
   
   # Clean BuildKit cache
   docker buildx prune -af
   
   # See disk_management.rst for more strategies

Builds Very Slow
~~~~~~~~~~~~~~~~

**Check cache:**

.. code-block:: bash

   # View cache usage
   du -sh /tmp/.buildx-cache
   
   # If > 5GB, prune:
   docker buildx prune -af

**Check builder:**

.. code-block:: bash

   docker buildx ls
   
   # Should show ada-builder with status "running"
   # If not:
   docker buildx create --name ada-builder --use --bootstrap

Using Legacy Builder
--------------------

If you can't install BuildX, you can use the legacy builder:

.. code-block:: bash

   # Add to ~/.bashrc
   export DOCKER_BUILDKIT=0
   export COMPOSE_DOCKER_CLI_BUILD=0
   
   # Then reload
   source ~/.bashrc
   
   # Build as normal
   docker compose build

**Drawbacks:**

- Slower builds (2-3x longer)
- Worse caching behavior
- No parallel builds
- Missing modern Dockerfile features

CI/CD Integration
-----------------

GitHub Actions (example):

.. code-block:: yaml

   - name: Set up Docker Buildx
     uses: docker/setup-buildx-action@v3
   
   - name: Build images
     run: docker compose build

BuildX is included in GitHub Actions runners by default.

Best Practices
--------------

1. **Run setup script first**: ``./scripts/setup_buildx.sh``
2. **Use named builder**: ``ada-builder`` (created by script)
3. **Keep .dockerignore updated**: Exclude unnecessary files
4. **Prune cache periodically**: ``docker buildx prune`` monthly
5. **Pull base images**: ``docker compose build --pull`` weekly

Performance Tips
----------------

**Speed up Python builds:**

.. code-block:: dockerfile

   # In Dockerfile, copy requirements first
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   # Then copy code (cached unless requirements change)
   COPY *.py .

**Speed up Node builds:**

.. code-block:: dockerfile

   # Copy package files first
   COPY package*.json .
   RUN npm install
   
   # Then copy source
   COPY . .

**Multi-stage builds:**

Use multi-stage builds to reduce final image size:

.. code-block:: dockerfile

   # Build stage
   FROM python:3.13 AS builder
   COPY requirements.txt .
   RUN pip wheel --no-cache-dir -r requirements.txt
   
   # Runtime stage
   FROM python:3.13-slim
   COPY --from=builder /wheels /wheels
   RUN pip install --no-cache /wheels/*.whl

BuildKit Statistics
-------------------

According to Docker surveys and package manager data:

- **Docker Desktop users**: ~95% have BuildX (included)
- **Linux docker-ce users**: ~40-60% have BuildX installed
- **Adoption growing**: +15-20% year-over-year

**Why not universal on Linux?**

- Separate package (``docker-buildx-plugin``)
- Not always in default install
- Users may have older setups
- Some distros lag behind

This is why Ada includes setup tools - we want everyone to have the best experience!

See Also
--------

- :doc:`getting_started` - Initial setup guide
- :doc:`disk_management` - Disk space optimization
- :doc:`development` - Development workflow
- `Docker BuildX Documentation <https://docs.docker.com/build/>`_
