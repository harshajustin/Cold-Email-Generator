import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-70b-versatile")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, name, link):
        """
        Generates a cold email based on the provided job description, user's name, and optional portfolio link.

        Args:
            job (str): The job description for which the email is being generated.
            name (str): The user's name, used for personalization in the email.
            link (str, optional): The user's portfolio link, to be included in the email if provided.

        Returns:
            str: The generated email content.
        """
        
        # Add portfolio instruction if link is provided
        portfolio_instruction = (
            f"Include a link to your portfolio at a natural point in the email: {link}." 
            if link else ""
        )
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are {name}, a proactive and ambitious recent graduate eager to contribute to solving client challenges. 
            Your task is to write a concise, professional, and persuasive cold email to the client regarding the job mentioned above. 
            Highlight your enthusiasm, relevant skills, and how you can help them achieve their goals. 
            {portfolio_instruction}
            Do not include extraneous details such as contact information. Be direct, specific, and impactful.
            
            ### EMAIL (NO PREAMBLE):
            """
        )
        chain_email = prompt_email | self.llm
        response = chain_email.invoke({
            "job_description": str(job),
            "name": name,
            "portfolio_instruction": portfolio_instruction,
            "Portfolio_link": link or "",
        })

        return response.content
