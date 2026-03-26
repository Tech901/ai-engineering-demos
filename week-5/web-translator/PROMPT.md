# Web Translator Tool

This is a web-based tool that lets me explor the Azure AI Translate service. It should have an option to select an
input language and an output language. It should include a textarea that lets me type content for the input language.

There should be a button that lets me "Translate" the input text, and see the resulting translation.

Because I'm a developer who is interested in how the API works, I want to see a panel that includes the JSON payload
for both the HTTP Request as well as the HTTP Response that we get back from the API.

## Resources

* [List of supported languages](https://learn.microsoft.com/en-us/azure/ai-services/translator/language-support)
* [Azure AI Translate REST api docs](https://learn.microsoft.com/en-us/azure/ai-services/translator/document-translation/reference/rest-api-guide)
* [AI Translate Synchronous API document](https://learn.microsoft.com/en-us/azure/ai-services/translator/document-translation/reference/translate-document)

## Tools and programming languages

Here are the programming tools and languages that we want to use.

1. Python -- write all backend web code in python
2. CSS - Use the paper.css framework for web styling (see: https://www.getpapercss.com/)
3. FastAPI -- Use the fast api framework for handling http requests and rendering html documents; see: https://fastapi.tiangolo.com/
4. We'll continue to use uv to manage dependencies and run the project.
