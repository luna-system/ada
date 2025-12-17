==================
Disk Management
==================

Ada's stack requires adequate disk space for Docker images, models, and runtime data. This guide helps you monitor and manage disk usage.

.. contents:: On This Page
   :local:
   :depth: 2

Disk Requirements
-----------------

**Minimum:** 20GB free space

**Recommended:** 50GB+ free space

**Why?**

- Docker images: ~5-10GB (brain, frontend, chroma, ollama base)
- Ollama models: 10-20GB each (DeepSeek R1: ~15GB, Llama 3.2: ~2GB)
- Runtime data: 1-5GB (ChromaDB vectors, conversation history, backups)
- Headroom: 10GB+ for updates and temporary files

**Large models warning:** Models like DeepSeek R1 can be 15-20GB each. If you switch between multiple models, you may need 50GB+ just for model storage.

Monitoring Disk Usage
----------------------

Check Current Usage
~~~~~~~~~~~~~~~~~~~

Run the provided monitoring script::

    ./scripts/check_disk_space.sh

This shows:

- Current disk usage percentage
- Available space remaining
- Warnings at 80% and 90% thresholds
- Ada-specific usage breakdown
- Docker system usage
- Actionable cleanup commands

Example output::

    💾 Disk Usage: 75%
    📊 Available: 45.2G / 180.0G
    
    Ada Usage:
      ./data/               2.1GB
      Docker images:        8.3GB
      Docker containers:    0.5GB
    
    ✅ Disk space healthy

**Warning triggers:**

- **80% full** - ⚠️ Warning: Consider cleanup soon
- **90% full** - 🚨 Critical: Cleanup needed immediately

Check Specific Directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check Docker usage::

    docker system df

Check Ada data directories::

    du -sh ./data/*

Check individual model sizes::

    docker exec ada-v1-ollama-1 ollama list

Cleanup Strategies
------------------

Quick Wins (Immediate)
~~~~~~~~~~~~~~~~~~~~~~

**1. Remove unused Docker resources**::

    # Show what will be removed (dry run)
    docker system prune -a --volumes --dry-run
    
    # Remove unused images, containers, volumes, networks
    docker system prune -a --volumes

Expected savings: **50-100GB** (if you have many old images)

**2. Clean old backups**::

    ./scripts/cleanup_old_backups.sh

This removes backup files older than 7 days from ``./data/backups/``.

Expected savings: **100MB-1GB**

**3. Remove unused Ollama models**::

    # List installed models
    docker exec ada-v1-ollama-1 ollama list
    
    # Remove a specific model
    docker exec ada-v1-ollama-1 ollama rm MODEL_NAME

Expected savings: **2-20GB per model**

Example: Removing an unused DeepSeek R1 variant saves ~15GB.

Medium-Term (Scheduled)
~~~~~~~~~~~~~~~~~~~~~~~

**1. Log rotation** (already configured)

Ada automatically rotates logs to prevent indefinite growth:

- Max file size: 10MB
- Max files: 3 per service
- Total log storage: ~150MB max

Configured in ``compose.yaml`` via ``x-logging`` anchor.

**2. Periodic backup cleanup**

Run weekly::

    ./scripts/cleanup_old_backups.sh

Or add to cron::

    # Weekly cleanup (Sundays at 3am)
    0 3 * * 0 cd /path/to/ada-v1 && ./scripts/cleanup_old_backups.sh

**3. Review installed models**

Monthly, audit your models::

    docker exec ada-v1-ollama-1 ollama list

Remove models you're not actively using.

Long-Term (Optimization)
~~~~~~~~~~~~~~~~~~~~~~~~

**1. Use quantized models**

Smaller quantized models save significant space:

- ``deepseek-r1:7b`` (4GB) vs ``deepseek-r1:70b`` (40GB)
- ``llama3.2:1b`` (1GB) vs ``llama3.2:70b`` (40GB)

Trade-off: Smaller models = less capable, but often sufficient.

**2. Shared Ollama instance**

Run Ollama separately and point multiple Ada instances to it::

    # In .env or compose.yaml
    LLM_BASE_URL=http://shared-ollama:11434

Benefit: Multiple Ada deployments share one model library.

**3. Multi-stage Docker builds**

Future optimization: Reduce image sizes by 30-50% using multi-stage builds.

Tracked in: ``.ai/DISK_OPTIMIZATION.md``

Troubleshooting
---------------

"Disk is full" error
~~~~~~~~~~~~~~~~~~~~

**Symptom:** Commands fail with "No space left on device"

**Immediate fix:**

1. Run ``docker system prune -a --volumes`` to free 50-100GB
2. Check model sizes: ``docker exec ada-v1-ollama-1 ollama list``
3. Remove unused models

**Prevention:**

- Run ``./scripts/check_disk_space.sh`` weekly
- Set up monitoring alerts at 80% usage

Services won't start after cleanup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Docker Compose fails to start services after ``docker system prune``

**Cause:** Prune removed images needed by Ada

**Fix:** Rebuild images::

    docker compose build
    docker compose up -d

This re-downloads/rebuilds needed images (~5-10 minutes).

Models disappeared after prune
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Ollama models missing after ``docker system prune -a --volumes``

**Cause:** ``--volumes`` flag removed the Ollama volume

**Fix:** Re-pull your model::

    docker exec ada-v1-ollama-1 ollama pull deepseek-r1:latest

**Prevention:** Omit ``--volumes`` flag unless you know you want to delete data::

    docker system prune -a  # Safe: keeps volumes

Maintenance Schedule
--------------------

**Daily** (automated)

- Log rotation (automatic via Docker)

**Weekly**

- Check disk usage: ``./scripts/check_disk_space.sh``
- Clean old backups: ``./scripts/cleanup_old_backups.sh``

**Monthly**

- Review installed models: ``docker exec ada-v1-ollama-1 ollama list``
- Consider removing unused models
- Review Docker images: ``docker images``

**Quarterly**

- Full audit: ``docker system df -v``
- Consider model optimizations (quantization)
- Review data retention policies

Best Practices
--------------

**1. Monitor proactively**

Don't wait for disk full errors. Check weekly::

    ./scripts/check_disk_space.sh

**2. Clean incrementally**

Small regular cleanups > occasional massive pruning::

    # Weekly: Just old backups (safe, fast)
    ./scripts/cleanup_old_backups.sh
    
    # Monthly: Unused Docker images (safe)
    docker image prune -a
    
    # As needed: Full prune (aggressive)
    docker system prune -a

**3. Plan model storage**

Before pulling a large model, check available space::

    df -h /
    docker exec ada-v1-ollama-1 ollama list

If you're tight on space, consider a smaller quantized model.

**4. Document your models**

Keep notes on which models you're actively using::

    # In your own notes/wiki
    - deepseek-r1:latest (primary, 15GB) - Use for complex reasoning
    - llama3.2:3b (backup, 2GB) - Use for simple tasks

Makes cleanup decisions easier.

**5. Use .dockerignore**

All Ada services include ``.dockerignore`` files to prevent copying unnecessary files into Docker images. This saves 10-50MB per image.

If you add custom services, create ``.dockerignore`` files for them.

Advanced Topics
---------------

Docker Storage Drivers
~~~~~~~~~~~~~~~~~~~~~~~

Docker's storage driver affects disk usage. Check yours::

    docker info | grep "Storage Driver"

**overlay2** (default on modern Linux): Efficient, good performance.

**vfs** (fallback): Inefficient, uses more disk space.

If you're on ``vfs``, consider switching to ``overlay2`` if possible (requires kernel support).

Disk Usage Warnings in UI
~~~~~~~~~~~~~~~~~~~~~~~~~~

Future enhancement: Ada could display disk warnings in the web UI.

Tracked in: ``.ai/DISK_OPTIMIZATION.md`` under "User-Facing Warnings"

External Volume Storage
~~~~~~~~~~~~~~~~~~~~~~~

For very constrained systems, mount ``./data/ollama`` on external storage::

    # In compose.yaml, change:
    volumes:
      - ./data/ollama:/root/.ollama
    
    # To:
    volumes:
      - /mnt/external/ada/ollama:/root/.ollama

Models live on external drive, freeing up main disk.

See Also
--------

- :doc:`configuration` - General configuration options
- :doc:`hardware` - Hardware requirements and optimization
- :doc:`sbc` - Single-board computer (Raspberry Pi, etc.) setup
- ``.ai/DISK_OPTIMIZATION.md`` - Technical deep dive (for developers)

Summary
-------

**Key takeaways:**

✅ **Monitor:** Run ``./scripts/check_disk_space.sh`` weekly

✅ **Clean regularly:** Use ``./scripts/cleanup_old_backups.sh`` and ``docker system prune``

✅ **Plan ahead:** Check space before pulling large models

✅ **Use quantized models:** Save 50-80% space with minimal quality loss

✅ **Log rotation:** Already configured, no action needed

Following these practices prevents "surprise disk full" situations and keeps Ada running smoothly! 💾✨
