# Python SDK for GroupDocs.Rewriter Cloud

![](https://img.shields.io/badge/api-v1.0-lightgrey) ![PyPI](https://img.shields.io/pypi/v/groupdocs-rewriter-cloud) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/groupdocs-rewriter-cloud) ![PyPI - Implementation](https://img.shields.io/pypi/implementation/groupdocs-rewriter-cloud) ![PyPI - Wheel](https://img.shields.io/pypi/wheel/groupdocs-rewriter-cloud) [![GitHub license](https://img.shields.io/github/license/groupdocs-rewriter-cloud/groupdocs-rewriter-cloud-python)](https://github.com/groupdocs-rewriter-cloud/groupdocs-rewriter-cloud-python/blob/master/LICENSE)

[Product Page](https://products.groupdocs.cloud/rewriter/python/) | [Documentation](https://docs.groupdocs.cloud/rewriter/) | [Demos](https://products.groupdocs.app/rewriter/family) | [Swagger UI](https://apireference.groupdocs.cloud/rewriter/) | [Examples](https://github.com/groupdocs-rewriter-cloud/groupdocs-rewriter-cloud-python) | [Blog](https://blog.groupdocs.cloud/category/rewriter/) | [Search](https://search.groupdocs.cloud/) | [Free Support](https://forum.groupdocs.cloud/c/rewriter) | [Free Trial](https://purchase.groupdocs.cloud/trial)

[GroupDocs.Rewriter Cloud](https://products.groupdocs.cloud/rewriter/) is an easy-to-use and versatile online service for rephrasing the content of Microsoft Word, Open Office, PDF, and plain text documents with full preservation of their meaning. A powerful neural network reads and understands the text and then paraphrases it with different wording, producing a plagiarism-free result. While the background process is very complex and resource-intensive, you do not have to worry about formulas, machine learning, and load - our cloud services do all the work by providing you with a REST API to interact with them.

This software development kit (SDK) simplifies the interaction with GroupDocs.Rewriter Cloud API from Python code, allowing you to focus on the task at hand rather than the technical details. It handles all the routine operations such as establishing connection, sending API requests, and parsing responses, wrapping all these tasks into a few lines of code that are very easy to read and maintain even for inexperienced developers.

## Before you begin

GroupDocs.Rewriter Cloud is an on-demand service. As such, it has no specific hardware or operating system requirements. In order to use the service, you must create an account at GroupDocs Cloud API:

1. Go to https://dashboard.groupdocs.cloud/
2. If you are already registered with Aspose, sign in with your user name and password.  
   Otherwise, click Don’t have an account? Sign Up link and create a new account.
3. [Check out](https://docs.groupdocs.cloud/translation/subscription/) more information about available subscription plans and a free tier limits.

GroupDocs values your privacy and takes technical, security and organizational measures to protect your data from unauthorized use, accidental loss or disclosure. Read our [Privacy Policy](https://about.groupdocs.cloud/legal/privacy-policy/) and [Terms of Service](https://about.groupdocs.cloud/legal/tos/) for details.

## How it works

Provide the file in one of the supported formats or a plain text. GroupDocs.Rewriter Cloud API will rephrase it and save the rewritten file to our cloud, or just return the paraphrased text.

## Supported formats

GroupDocs.Rewriter Cloud can rephrase documents in the most popular formats.

Document | Extensions | Description
-------- | ---------- | -----------
Microsoft Word | .DOCX<br />.DOCM<br />.DOC<br />.RTF | Microsoft Word 97-2021 and Microsoft 365 Word documents, including macro-enabled documents.
Portable Document Format | .PDF | An open standard cross-platform format for documents that include formatted text, images, multimedia elements, and more.
OpenDocument Text | .ODT | Documents created with a number of open source word processing applications, such as Writer from Apache OpenOffice and LibreOffice.
Plain text | .TXT | Plain text files or text in the form of lines.

In addition to rephrasing, GroupDocs.Rewriter Cloud can save the resulting document in various file formats other than the original, with formatting preserved (where applicable).

Source file format | Paraphrased file format
------------------ | ----------------------
.DOCX              | .DOCX<br />.RTF<br />.HTML<br />.ODT<br />.TXT<br />.MD<br />.PDF<br />.TIFF<br />.SVG<br />.XPS
.DOC               | .DOC<br />.DOCX<br />.RTF<br />.HTML<br />.ODT<br />.TXT<br />.MD<br />.PDF<br />.TIFF<br />.SVG<br />.XPS
.ODT               | .DOCX<br />.RTF<br />.HTML<br />.ODT<br />.TXT<br />.MD<br />.PDF<br />.TIFF<br />.SVG<br />.XPS
.RTF               | .DOCX<br />.RTF<br />.HTML<br />.ODT<br />.TXT<br />.MD<br />.PDF<br />.TIFF<br />.SVG<br />.XPS
.PDF               | .DOCX<br />.PPTX<br />.HTML<br />.XPS<br />.SVG

## Supported languages

- **en** — to paraphrase English text or document
- **ru** — to paraphrase Russian text or document

## Quick start

To start using GroupDocs.Rewriter Cloud in your Python applications, follow a few simple steps:

## System requirements

Supported versions of Python:

- 2.7
- 3
- 3.4
- 3.5
- 3.6
- 3.7
- 3.8

See [requirements.txt](requirements.txt) for the list of dependencies.

## Getting an access token

The GroupDocs.Rewriter Cloud API is fully compliant with industry security standards and best practices. Data transfer is carried out using JWT authentication, which eliminates all possibilities of data theft or disclosure.

To obtain a JWT token, get the _Client ID_ and _Client Secret_ credentials:

1. Sign in to [GroupDocs Cloud API Dashboard](https://dashboard.groupdocs.cloud/).
2. Go to [**Applications**](https://dashboard.groupdocs.cloud/applications) page.
3. Create the `samples` storage for exchanging files by clicking the _plus_ icon and following the required steps.
4. Provide the application name.
5. Click **Save** button.
6. Click the newly created application and copy the values from **Client Id** and **Client Secret** fields. These credentials can be used to access all GroupDocs Cloud services.

Now request an access token with the following API call:

```bash
curl --location --request POST 'https://api.groupdocs.cloud/connect/token' \
     --header 'Content-Type: application/x-www-form-urlencoded' \
     --data-urlencode 'grant_type=client_credentials' \
     --data-urlencode 'client_id=CLIENT-ID-VALUE' \
     --data-urlencode 'client_secret=CLIENT-SECRET-VALUE'
```

You should get a response that looks something like this:

```json
{
	"access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...Iwr6g2zbFwf1nLtg",
	"expires_in": 3600,
	"token_type": "Bearer"
}
```
The access token will be valid for the number of seconds specified in the `expires_in` property. If it has expired, request a new one using the same credentials.

### Installing GroupDocs.Rewriter Python SDK

Install **groupdocs-rewriter-cloud** package with [PIP](https://pypi.org/project/pip/) from [PyPI](https://pypi.org/) by executing the following command:

```sh
pip install groupdocs-rewriter-cloud
```

Alternatively, you can clone the repository and install it via [Setuptools](http://pypi.python.org/pypi/setuptools):

```sh
python setup.py install
```

### Running a demo project

- Get the SDK.
- Set your client\_id & client\_secret credentials.
- Run **Jupyter** notebook [demo.ipynb](https://github.com/groupdocs-rewriter-cloud/groupdocs-rewriter-cloud-python/blob/master/demo.ipynb)

#### Demo project structure

Component | Type | Description
--------- | ---- | -----------
**groupdocsrewritercloud** | Module | Python SDK for GroupDocs.Rewriter Cloud
**test** | Module | Unit tests
**demo** | Notebook | Sample Jupyter notebook

## Examples

The following code snippets demonstrate how to use the GroupDocs.Rewriter Python SDK to accomplish various tasks.

### Rewrite a text

```python
# Load the gem
import groupdocs_rewriter_cloud
# Get Client Id and Client Secret from https://dashboard.groupdocs.cloud
my_client_id = ""
my_client_secret = ""

# Create instance of the API
configuration = Configuration(apiKey=my_client_secret, appSid=my_client_id)
api = RewriterApi(configuration)

language = "en"
text = "GroupDocs Cloud customers come from a wide variety of industries and can be found all over the globe."

rewriter = RewriteText(language, text)
request = rewriter.to_string()
res_text = api.post_rewrite_text(request)
print(res_text.message)
```

### Rewrite a Word document

```python
# Load the gem
import groupdocs_rewriter_cloud
# Get Client Id and Client Secret from https://dashboard.groupdocs.cloud
my_client_id = ""
my_client_secret = ""

# Create instance of the API
configuration = Configuration(apiKey=my_client_secret, appSid=my_client_id)
api = RewriterApi(configuration)

# Document paraphrasing
language = "en"
_format = "docx"
storage = "internal"
name = "test_python.docx"
folder = ""
savepath = ""
savefile = "test_python.docx"  
masters = False
elements = []
rewriter = RewriteDocument(language, _format, storage, name, folder, savepath, savefile, masters, elements)
request = rewriter.to_string()
res_doc = api.post_rewrite_document(request)
print(res_doc.message)
```

## Other SDKs for GroupDocs.Rewriter Cloud

GroupDocs also offers native SDK packages for other popular programming languages:

### .NET

- [NuGet](https://www.nuget.org/packages/GroupDocs.Rewriter-Cloud/)
- [GitHub](https://github.com/groupdocs-rewriter-cloud/groupdocs-rewriter-cloud-dotnet)

---

[Product Page](https://products.groupdocs.cloud/rewriter/dotnet/) | [Docs](https://docs.groupdocs.cloud/rewriter/) | [Demos](https://products.groupdocs.app/rewriter/family) | [Swagger UI](https://apireference.groupdocs.cloud/rewriter/) | [Examples](https://github.com/groupdocs-rewriter-cloud/groupdocs-rewriter-cloud-dotnet) | [Blog](https://blog.groupdocs.cloud/category/rewriter/) | [Search](https://search.groupdocs.cloud/) | [Free Support](https://forum.groupdocs.cloud/c/rewriter) | [Free Trial](https://purchase.groupdocs.cloud/trial)
