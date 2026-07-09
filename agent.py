from anthropic import Anthropic
from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
base_url = os.getenv("DIET_API_BASE_URL")

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

tools = [
  {
    "name" : "Create_Meal",
    "description" : "This tool will be called when a meal is being created",
    "input_schema" : {
      "type" : "object",
      "properties" : {
        "name" : {"type" : "string", "description": "name of the meal"},
        "description" : {"type" : "string", "description": "brief description about the meal, how much and what they ate."},
        "date_time" : {"type" : "string", "description": "date and time that the person ate the meal. Format example: 2026-05-07 14:30:00"},
        "on_diet" : {"type": "string", "enum": ["yes", "no"] ,"description": "Wheter the meal is on the diet or not"},
      },
    "required": ["name", "description", "date_time", "on_diet"]
    },
  },
  {
    "name": "Get_Meal",
    "description": "This tool will get the meal data using its ID from the database and display to the user",
    "input_schema": {
      "type": "object",
      "properties": {
        "id_meal": {"type": "integer", "description": "The unique ID of the meal to retrieve."}
      },
    "required": ["id_meal"]
    },
  },
  {
    "name": "Delete_Meal",
    "description": "This tool will delete a meal from the database after the user input its ID.",
    "input_schema": {
      "type": "object",
      "properties": {
        "id_meal" : {"type": "integer", "description": "The unique ID of the meal to delete."},
      },
      "required": ["id_meal"]
    },
  },
  {
    "name": "Update_Meal",
    "description": "This tool will update a meal information from the database after the user input its ID.",
    "input_schema": {
      "type": "object",
      "properties": {
        "id_meal" : {"type": "integer", "description": "The unique ID of the meal to update."},
        "name" : {"type" : "string", "description": "name of the meal"},
        "description" : {"type" : "string", "description": "brief description about the meal, how much and what they ate."},
        "date_time" : {"type" : "string", "description": "date and time that the person ate the meal. Format example: 2026-05-07 14:30:00"},
        "on_diet" : {"type": "string", "enum": ["yes", "no"] ,"description": "Wheter the meal is on the diet or not"}, 
      },
      "required": ["id_meal", "name", "description", "date_time", "on_diet"]
    },
  },
  {
    "name" : "Read_Meals",
    "description" : "This tool will get and list all the meals that are stored on the database.",
    "input_schema": {
      "type": "object",
      "properties": {

      }
    }
  }
]

def execute_tool(tool_name, tool_input):
  if tool_name == "Create_Meal":
    response = requests.post(
      f"{base_url}/meal",
      json=tool_input
    )

    if response.status_code < 400:
      result = {"success" : True, "data": response.json()}
    else:
      result = {"success": False, "data": response.json()}

    return result

  elif tool_name == "Get_Meal":
    response = requests.get(
      f"{base_url}/meal/{tool_input['id_meal']}"
    )

    if response.status_code < 400:
      result = {"success": True, "data": response.json()}
    else:
      result = {"success": False, "data": response.json()}
    
    return result
  
  elif tool_name == "Delete_Meal":
    response = requests.delete(
      f"{base_url}/meal/{tool_input['id_meal']}"
    )

    if response.status_code < 400:
      result = {"success": True, "data": response.json()}
    else:
      result = {"success": False, "data": response.json()}
    
    return result
  
  elif tool_name == "Update_Meal":
    id_meal = tool_input['id_meal']
    body = dict(tool_input)
    body.pop("id_meal")
    response = requests.put(
      f"{base_url}/meal/{id_meal}",
      json=body
    )

    if response.status_code < 400:
      result = {"success": True, "data": response.json()}
    else:
      result = {"success": False, "data": response.json()}

    return result
  
  elif tool_name == "Read_Meals":
    response = requests.get(
      f"{base_url}/meal"
    )

    if response.status_code < 400:
      result = {"success": True, "data": response.json()}
    else:
      result = {"success": False, "data": response.json()}

    return result



messages = []

while True:
  user_input = input("Você: ")

  if user_input.lower() == "sair":
    break

  messages.append({"role": "user", "content": user_input})

  while True:
    response = client.messages.create(
      model="claude-sonnet-4-5",
      max_tokens=1024,
      tools=tools,
      tool_choice={"type" : "auto", "disable_parallel_tool_use" :   True},
      messages=messages
    )

    if response.stop_reason == "tool_use":
      for block in response.content:
        if block.type == "tool_use":
          tool_id = block.id
          tool_name = block.name
          tool_input = block.input

      tool_result = execute_tool(tool_name, tool_input)

      messages.append(
        {"role": "assistant", "content": response.content},
      )

      messages.append(
        {
          "role" : "user",
          "content": [
            {
              "type": "tool_result",
              "tool_use_id": tool_id,
              "content": str(tool_result)
            }
          ]
        }
      )
    else:
      print(response.content[0].text)
      messages.append({"role": "assistant", "content": response.content})
      break
