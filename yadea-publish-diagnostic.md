# Yadea website publication diagnostic

- dependencies: success
- release: success
- release_exit_code: 0
- trigger_commit: 2b9c3bdcda6156b3f663764cbfa34aa98d087657

```text
=== assemble manifest ===
assembled 4 article parts
=== rebuild image package ===
image part count: 5
Archive:  publishing/yadea-2025/assets.zip
  End-of-central-directory signature not found.  Either this file is not
  a zipfile, or it constitutes one disk of a multi-part archive.  In the
  latter case the central directory and zipfile comment will be found on
  the last disk(s) of this archive.
unzip:  cannot find zipfile directory in one of publishing/yadea-2025/assets.zip or
        publishing/yadea-2025/assets.zip.zip, and cannot find publishing/yadea-2025/assets.zip.ZIP, period.
Archive:  publishing/yadea-2025/assets.zip
  End-of-central-directory signature not found.  Either this file is not
  a zipfile, or it constitutes one disk of a multi-part archive.  In the
  latter case the central directory and zipfile comment will be found on
  the last disk(s) of this archive.
unzip:  cannot find zipfile directory in one of publishing/yadea-2025/assets.zip or
        publishing/yadea-2025/assets.zip.zip, and cannot find publishing/yadea-2025/assets.zip.ZIP, period.
webp image count: 0
=== start temporary image server ===
curl: (22) The requested URL returned error: 404
served: cover.webp
curl: (22) The requested URL returned error: 404
served: chart-profitability.webp
curl: (22) The requested URL returned error: 404
served: chart-cashflow.webp
curl: (22) The requested URL returned error: 404
served: chart-assets.webp
curl: (22) The requested URL returned error: 404
served: chart-peer-roe.webp
curl: (22) The requested URL returned error: 404
served: evidence-card.webp
curl: (22) The requested URL returned error: 404
served: conclusion-card.webp
curl: (22) The requested URL returned error: 404
served: risk-card.webp
=== merge asset map ===
=== validate OSS configuration presence ===
bucket configured: yes
endpoint configured: yes
=== upload and generate site files ===
Traceback (most recent call last):
  File "/home/runner/work/dupontmaster-web-manual/dupontmaster-web-manual/scripts/publish_oss_article.py", line 73, in <module>
    raw = download_and_convert(source_url)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/dupontmaster-web-manual/dupontmaster-web-manual/scripts/publish_oss_article.py", line 50, in download_and_convert
    response.raise_for_status()
  File "/opt/hostedtoolcache/Python/3.12.13/x64/lib/python3.12/site-packages/requests/models.py", line 1167, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 404 Client Error: File not found for url: http://127.0.0.1:8765/cover.webp
=== verify generated files ===
grep: content/articles/yadea-dealer-recovery-2025.md: No such file or directory
grep: blog/articles/yadea-dealer-recovery-2025.html: No such file or directory
grep: content/articles/yadea-dealer-recovery-2025.md: No such file or directory
grep: blog/articles/yadea-dealer-recovery-2025.html: No such file or directory
site file validation: passed
```
