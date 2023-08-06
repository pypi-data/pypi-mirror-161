# Alliance Auth Template Overrides used by Sev3rance Alliance

# Sev3rance Auth Templates

Template Overrides for Alliance Auth

```shell
pip install sev3rance-auth-templates
```

In `local.py` right after `INSTALLED_APPS`:

```python
# -7- Auth Templates - https://github.com/sev3rance/sev3rance-auth-templates
INSTALLED_APPS.insert(0, "sev3rance_auth_templates")
```

**Important**

If you are using `AA-GDPR`, the template stuff needs to be **after** the `AA_GDPR`
entry, like this:

```python
# GDPR Compliance
INSTALLED_APPS.insert(0, "aagdpr")
AVOID_CDN = True

# -7- Auth Templates - https://github.com/sev3rance/sev3rance-auth-templates
INSTALLED_APPS.insert(0, "sev3rance_auth_templates")
```
