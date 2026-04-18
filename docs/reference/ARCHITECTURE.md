# KL1 / VimuttiOS Integrated Architecture (v6 meta–OS)

This document describes how the various historical stacks in `stacks/` are meant to
coexist under one conceptual OS.

## Layers

- **API / Backend**: KL1_OS_V3, KL1_Integrated_v1_1, UP-OS_v11_2_Alerts, YOS_FullStack, NovaChat backend.
- **Dashboards / Web**: KL1_FullStack_v1APP, KL1_Integrated_v1_1 frontend, YOS_ToL_v1_web.
- **Mobile Clients**: KL1_Superstack_iOS_Starter, KL1_APEX_iOS_Expo.
- **Practice / Retreat Engines**: upanisa_os_v9, SAMA_Ultimate_v4.
- **Meta-Tools**: NovaChat Pro (conversational layer), Yield-OS tooling, etc.

Rather than forcibly merging all codebases, v6 treats them as **modules** that can be:

1. Run independently as needed.
2. Gradually refactored into a more unified stack (shared auth, storage, telemetry).
3. Orchestrated together via Docker (see `integration/docker-compose.template.yml`).

## Recommended Evolution Path

1. Choose ONE primary backend (e.g. UP-OS_v11_2_Alerts or KL1_Integrated_v1_1) as the
   canonical API for new features.
2. Mount other stacks as:
   - specialized microservices (alerts, ToL reader, NovaChat),
   - or legacy apps migrated piece by piece.
3. Use the multi-agent mesh (`agents/kl1_agents.yaml`) to:
   - propose patch plans,
   - maintain architecture docs,
   - track which stack owns which feature.

This bundle is **conservative**: it preserves everything and adds a thin, opinionated
integration layer you can iterate on.
