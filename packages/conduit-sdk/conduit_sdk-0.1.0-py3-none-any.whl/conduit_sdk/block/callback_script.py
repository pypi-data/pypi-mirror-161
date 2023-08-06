import html
import json
from dataclasses import asdict

from .schema import ResponseSchema


def make_block_config_callback_script(origin: str, payload: ResponseSchema) -> str:
    prepared_payload = asdict(payload)
    tpl = '''
    <script type="text/javascript">
        (function() {{
            window.parent.postMessage({{
                'payload': JSON.stringify({payload})
            }}, '{origin}')
        }})()
    </script>
    '''  # noqa: JS101, JS102

    return tpl.format(
        origin=html.escape(origin),
        payload=json.dumps(prepared_payload),
    )
