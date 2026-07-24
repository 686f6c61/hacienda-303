# Adaptadores de plataforma

El mismo `SKILL.md`, los scripts y la base SQLite forman el núcleo común.

## OpenAI Codex

- Skill personal: `~/.codex/skills/clasificar-facturas-iva-aeat/`
- Metadatos nativos: `agents/openai.yaml`

## Claude Code

- Skill personal: `~/.claude/skills/clasificar-facturas-iva-aeat/`
- Agente personal: `~/.claude/agents/clasificador-facturas-iva-aeat.md`
- El agente precarga la skill mediante el campo `skills`.

## Kimi Code

- Skill personal: `~/.kimi-code/skills/clasificar-facturas-iva-aeat/`
- Agente personal: `~/.kimi-code/agents/clasificador-facturas-iva-aeat-kimi.md`
- La definición no fija el modelo para seguir funcionando con Kimi K3 o con el modelo activo configurado.

## GLM 5.2

GLM 5.2 se usa mediante distintos hosts compatibles. Instalar el núcleo y el agente en el directorio del host:

- con Claude Code: usar las ubicaciones de Claude y seleccionar GLM 5.2 en la configuración del proveedor;
- con un host compatible con agentes Markdown: usar `agents/glm-5.2.md` como prompt de sistema;
- si el host solo admite un prompt: pegar el cuerpo del agente y adjuntar o montar la carpeta de la skill.

No guardar claves API dentro de la skill o de los agentes.
