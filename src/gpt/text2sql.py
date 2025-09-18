import os
import json
from pathlib import Path
from typing import List

from langchain_core.messages import AnyMessage
from langgraph.prebuilt import create_react_agent
from langchain_community.utilities import SQLDatabase
from langchain_openai import AzureChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from src.prompt.text2sql import SYSTEM_PROMPT

class Text2SQLAgent:
    def __init__(self):
        # Sử dụng mô hình ngôn ngữ lớn - LLM
        # Ở đây là sử dụng GPT-4o-mini
        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_LLM_DEPLOYMENT_NAME"],
            azure_endpoint=os.environ["AZURE_ENDPOINT"],
            api_version=os.environ["AZURE_API_VERSION"],
            api_key=os.environ["AZURE_API_KEY"],
            max_tokens=32768,
            max_retries=3,
        )

        self.db_path = None
        self.agent_executor = None


    def run(self, query: str, db_path: str) -> List[AnyMessage]:
        # Bắt đầu chạy
        db_path = Path(db_path)
        
        if db_path != self.db_path:
            # \Desktop\Workspace\UTH_Python_CK\data\example.db"
            # db_path đang sử dụng dấu "\" nên có thể gặp lỗi
            # phải đổi lại thành dấu "/"
            # vậy nên đưa db_path đang là string trở thành 1 đối tượng của lớp Path có thể giúp giải quyết vấn đề này như sau:
            # sử dụng phương thức as_posix của lớp Path sẽ thay đổi "/" trong db_path thành "\
            
            # Kết nối CSDL
            db = SQLDatabase.from_uri(f"sqlite:///{db_path.as_posix()}")

            # Toàn bộ bên dưới là code mẫu nằm trong đường link
            # https://python.langchain.com/docs/tutorials/sql_qa/#initializing-agent
            toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)

            tools = toolkit.get_tools()

            agent_executor = create_react_agent(
                model=self.llm,
                tools=tools,
                prompt=SYSTEM_PROMPT
            )

            # Gán lại để sử dụng cho lần sau nếu sử dụng cùng 1 file .DB
            self.db_path = db_path
            self.agent_executor = agent_executor

        output = self.agent_executor.invoke(
            {"messages": [{"role": "user", "content": query}]}
        )

        messages: List[AnyMessage] = output["messages"]

        query = None
        for message in messages:
            if message.additional_kwargs.get("tool_calls"):
                function = message.additional_kwargs.get("tool_calls")[0]["function"]
                function_name = function.get("name")
                if function_name == "sql_db_query":
                    query = json.loads(function.get("arguments")).get("query")

        return messages, query