import os
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI, AsyncAssistantEventHandler,  OpenAIError, AzureOpenAI, AsyncAzureOpenAI



load_dotenv() 

try:
            
      async_openai_client = AsyncAzureOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version="2024-05-01-preview"
      )
      
      sync_openai_client = AzureOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version="2024-05-01-preview"
      )
      

    

      assistant = sync_openai_client.beta.assistants.retrieve(os.environ.get("AZURE_OPENAI_ASSISTANT_ID"))
      
      #Cambia el nombre del asistente
      #my_updated_assistant = sync_openai_client.beta.assistants.update(assistant_id="asst_qavU1q2xOM93rag16rKHZmYX", name='QAgent POC')
      #print(my_updated_assistant.name)
    
      # Actualiza las herramientas del asistente
      
          
      true = True
      false = False     
    
      tools_list = [
   {
      "type":"function",
      "function":{
         "name":"draw_plotly_chart",
         "description":"Dibuja un gráfico de Plotly basado en la figura JSON proporcionada y lo muestra con un mensaje adjunto.",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "message",
               "plotly_json_fig"
            ],
            "properties":{
               "message":{
                  "type":"string",
                  "description":"El mensaje que se mostrará junto al gráfico"
               },
               "plotly_json_fig":{
                  "type":"string",
                  "description":"Una cadena JSON que representa la figura de Plotly que se dibujará"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"getCurrentDate",
         "description":"Retorna la fecha y hora de hoy",
         "strict":false,
         "parameters":{
            "type":"object",
            "properties":{
               
            },
            "additionalProperties":false,
            "required":[
               
            ]
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"send_mail",
         "description":"Envía un correo",
         "strict":false,
         "parameters":{
            "type":"object",
            "properties":{
               "email":{
                  "type":"string",
                  "description":"Correo electrónico del destinatario"
               },
               "nombre":{
                  "type":"string",
                  "description":"Nombre del destinatario"
               },
               "texto":{
                  "type":"string",
                  "description":"Texto del correo"
               }
            },
            "required":[
               "email",
               "nombre",
               "texto"
            ],
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"getdataMSQL",
         "description":"Busca datos en la base de datos MySql",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "consulta"
            ],
            "properties":{
               "consulta":{
                  "type":"string",
                  "description":"consulta mysql autogenerada por el modelo"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"clima_actual",
         "description":"Proporciona el clima actual para una ciudad en particular",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "ciudad"
            ],
            "properties":{
               "ciudad":{
                  "type":"string",
                  "description":"Ciudad para la cual se requiere conocer el estado del clima actual"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"pronostico",
         "description":"Proporciona el pronostico del clima para una ciudad en particular",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "ciudad"
            ],
            "properties":{
               "ciudad":{
                  "type":"string",
                  "description":"Ciudad para la cual se requiere conocer el pronostico del clima"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"web_search",
         "description":"Busca información en la web sobre temas que son relevantes para el usuario",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "user_query"
            ],
            "properties":{
               "user_query":{
                  "type":"string",
                  "description":"La consulta del usuario"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"video_tool",
         "description":"Despliega videos en el front",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "message",
               "name",
               "url"
            ],
            "properties":{
               "message":{
                  "type":"string",
                  "description":"Breve descripción del video"
               },
               "name":{
                  "type":"string",
                  "description":"Nombre del video"
               },
               "url":{
                  "type":"string",
                  "description":"url del video"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"get_mysql_schema",
         "description":"Consulta el esquema de la tabla a consultar, retorna nombre de los campos, comentarios de los campos",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "table"
            ],
            "properties":{
               "table":{
                  "type":"string",
                  "description":"La tabla a consultar"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"busca_rut_cliente",
         "description":"Retorna el rut del cliente a partir del nombre del cliente para ser usado en el informe del cliente",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "razon_social"
            ],
            "properties":{
               "razon_social":{
                  "type":"string",
                  "description":"Razon social o también llamada Nombre del cliente"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"segmenta_cliente",
         "description":"Herramienta para segmentar al cliente. Retorna tipo_de_cliente, segmento, subsegmento, comuna_despacho. Para el informe del cliente",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "rut"
            ],
            "properties":{
               "rut":{
                  "type":"string",
                  "description":"Rut del cliente"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"busca_sku",
         "description":"Herramienta para consultar los sku comprados por el cliente. Para el informe del cliente",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "rut"
            ],
            "properties":{
               "rut":{
                  "type":"string",
                  "description":"Rut del cliente"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"faiss_ai_search",
         "description":"Busca información en la base vectorial FAISS que proviene de PDFS",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "consulta"
            ],
            "properties":{
               "consulta":{
                  "type":"string",
                  "description":"consulta del usuario en busca de información"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"getdataASQLS",
         "description":"Busca datos en la base de datos Azure SQL Server",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "consulta"
            ],
            "properties":{
               "consulta":{
                  "type":"string",
                  "description":"consulta SQL autogenerada por el modelo"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{

         "name":"getdataGSQLS",
         "description":"Busca datos en la base de datos GCP SQL Server",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "consulta"
            ],
            "properties":{
               "consulta":{
                  "type":"string",
                  "description":"consulta SQL autogenerada por el modelo"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{

         "name":"pdf_tool",
         "description":"Despliega pdf en un visor en el front",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "message",
               "name",
               "pdf"
            ],
            "properties":{
               "message":{
                  "type":"string",
                  "description":"Mensaje que acompaña al documento"
               },
               "name":{
                  "type":"string",
                  "description":"Nombre corto y descriptivo del documento"
               },
               "pdf":{
                  "type":"string",
                  "description":"documento pdf con extención .pdf Ej. documento.pdf"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"createDataFrame",
         "description":"Despliega un dataframe en el front cuando se le pasa un diccionario con la data",
         "strict":true,
          "parameters":{
            "type":"object",
            "required":[
               "message",
               "dataframe"
            ],
            "properties":{
               "message":{
                  "type":"string",
                  "description":"El mensaje que se mostrará junto al gráfico o la respuesta del agente"
               },
               "dataframe":{
                  "type":"string",
                  "description":"Dataframe a representar. El formato debe ser un diccionario con el siguiente formato: data = { 'Nombre_columna_1': [ 'Registro 1', 'Registro 2','Registro n' ], 'Nombre_columna_2': [1, 2, n]}"
               }
            },
            "additionalProperties":false
         }
      }
   },
   {
      "type":"function",
      "function":{
         "name":"recursos_conaf",
         "description":"Busca recursos Conaf más cercano al foco del siniestro.",
         "strict":true,
         "parameters":{
            "type":"object",
            "required":[
               "latitud", 
               "longitud"
            ],
            "properties":{
               "latitud":{
                  "type":"string",
                  "description":"latitud en Formato Decimal ejemplo '-30.222'"
               },
                "longitud":{
                  "type":"string",
                  "description":"longitud en Formato Decimal ejemplo '-70.21222'"
               }
            },
            "additionalProperties":false
         }
      }
   }
      ]

      my_updated_assistant = sync_openai_client.beta.assistants.update(
            assistant_id="asst_qavU1q2xOM93rag16rKHZmYX",           
            tools=tools_list,           
      )

    

except OpenAIError as e:
    print(f" --> 01 Error calling: {e}")
    
    
