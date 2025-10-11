import os, json
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAIError

def _to_dict(obj):
    # Hace robusta la conversión sin importar la versión del SDK
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "model_dump_json"):
        return json.loads(obj.model_dump_json())
    try:
        return json.loads(str(obj))
    except Exception:
        return obj

load_dotenv()

try:
    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-05-01-preview",
    )

    asst_id = os.environ["AZURE_OPENAI_ASSISTANT_ID"]
    assistant = client.beta.assistants.retrieve(asst_id)
    a = _to_dict(assistant)

    print(f"Assistant: {a.get('name','(sin nombre)')}  |  ID: {a.get('id')}")
    print(f"Modelo: {a.get('model')}")
    print(f"Descripción: {a.get('description','(sin descripción)')}")
    print("-" * 80)

    tools = a.get("tools", [])
    if not tools:
        print("Este assistant no tiene herramientas configuradas.")
    else:
        print(f"Total herramientas: {len(tools)}\n")
        for i, t in enumerate(tools, 1):
            t_type = t.get("type", "(desconocido)")
            print(f"{i}. type: {t_type}")

            # Si es una function tool, mostrar detalle
            if t_type == "function":
                fn = t.get("function", {})
                print(f"   name       : {fn.get('name')}")
                print(f"   description: {fn.get('description','')}")
                if "strict" in fn:
                    print(f"   strict     : {fn.get('strict')}")
                params = fn.get("parameters")
                if params:
                    print("   parameters :")
                    try:
                        print(json.dumps(params, ensure_ascii=False, indent=4))
                    except Exception:
                        print(f"      {params}")
            else:
                # Mostrar cualquier configuración adicional (p.ej. file_search, code_interpreter)
                extras = {k: v for k, v in t.items() if k != "type"}
                if extras:
                    print("   config     :")
                    try:
                        print(json.dumps(extras, ensure_ascii=False, indent=4))
                    except Exception:
                        print(f"      {extras}")
            print("-" * 80)

except OpenAIError as e:
    print(f"Error al consultar el Assistant: {e}")
except KeyError as e:
    print(f"Falta variable de entorno: {e}")
