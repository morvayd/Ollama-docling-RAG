#  Reference:  https://github.com/ollama/ollama-python
#  Author:  Daniel Morvay
#  Creator Email:  morvayd@gmail.com
#  Description:  Run on Windows, Linux, Mac - AI you can chat with, load a document then chat with the document.  

#
#  ---------- Install ----------
#

#  ----- Base Libraries -----
import datetime
import os
import platform
import random
import sys
import logging
import warnings
import math
import copy

#  ----- Additional Libraries -----
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
import ollama
from ollama import chat
from ollama import ChatResponse
from ollama import Client
import pandas
import sqlite3
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import EasyOcrOptions, PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions

#  ----- Custom Libraries -----
import PythonLog

#
#  ---------- Setup ----------
#
strPythonScript = "GPU-ollama-RAG.py"
strModified = "2025.12.17"

#  Python Version
strPyVer = platform.python_version()
#  OS - Windows or Linux or Mac
strOS = platform.system()
#  OS Version 
strOSVer = platform.platform()
#  PC Name
strPC = platform.node()
#  UserID
strUser = os.getlogin()
#  Filter warnings
warnings.filterwarnings('ignore')
#  Turn logging off
logging.disable(sys.maxsize)

#  Today's Date
strStartTime = datetime.datetime.today()
strDateNow = strStartTime.strftime("%Y.%m.%d")

#  IBM Granite Thinking [ "Yes" | "No" ]
strThink = "No"
#  Pirate personality [ "Yes" | "No" ]
strPirate = "No"
#  Jeeves personality [ "Yes" | "No" ]
strJeeves = "No"
#  Mystic personality [ "Yes" | "No" ]
strMystic = "No"

strLogPath = ""
strLogOut = ""

#  Initialize Text Colors
colorama_init(autoreset=True)
#  Colorama colors:  black, blue, cyan, green, magenta, red, reset, white, yellow
#  lightblack_ex, lightblue_ex, lightcyan_ex, lightgreen_ex, lightmagenta_ex, 
#  lightred_ex, lightwhite_ex, lightyellow_ex

#
#  ---------- Setup Docling ----------
#
if (strOS=="Darwin"):
    artifacts_path = "/Users/"+strUser+"/.cache/docling/models"
if (strOS=="Linux"):
    artifacts_path = "/home/"+strUser+"/.cache/docling/models"
if (strOS=="Windows"):
    artifacts_path = "/Users/"+strUser+"/.cache/docling/models"

accelerator_options = AcceleratorOptions(num_threads=8, device=AcceleratorDevice.CPU)
pipeline_options = PdfPipelineOptions(artifacts_path=artifacts_path)
pipeline_options.accelerator_options = accelerator_options

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

#
#  ---------- Python Log Start ----------
#
#  Note:  strLogPath, strLogOut are created & returned at the start of Logging
strReturn = PythonLog.PyLogStart(strPythonScript, strModified, strPyVer, strOS, strOSVer, strPC, strUser, strStartTime, strDateNow)

#  Load the Path and Filename from the function return
strLogPath = strReturn[0]
strLogOut = strReturn[1]

#
#  ---------- Setup Ollama ----------
#
#  Setup AI Tracking DB
strDBPath = "PythonLogAI"
strDBFile = strDBPath+"/"+strPC+"-AILog.db"

if (os.path.exists(strDBPath)!=True):
    os.makedirs(strDBPath)

def OllamaModel():
    #  Setup a model selector based on what has been downloaded.
    strOllama = list(ollama.list())

    #  If no models downloaded / installed, end
    if (len(strOllama[0][1])==0):
        print ("\n----- Error -----\nPlease use Ollama to download at least one LLM or SLM.\nCLI Example:  ollama pull granite3.2:2b")
        sys.exit("\nExiting Now, no language models installed.")

    strOllamaModel = []
    for i in range(0, len(strOllama[0][1])):
        strOllamaModel.append(strOllama[0][1][i]['model'])

    print ("\n---------- LLM Selection ----------")
    for i in range(0, len(strOllamaModel)):
        print (f"{Fore.RED}"+str(i)+f"{Style.RESET_ALL}: "+strOllamaModel[i])
    
    strChoose = input("\nPlease select the model number you would like to use. ")

    if (strChoose.isdigit()):
        if (int(strChoose) <= len(strOllamaModel)):
            strModel = strOllamaModel[int(strChoose)]  
        else:
            print (f"{Fore.RED}\nError: A number in this menu was not selected!\nChoosing a random model for you.{Style.RESET_ALL}")
            strModel = strOllamaModel[random.randrange(0, len(strOllamaModel))]
    else:
        print (f"{Fore.RED}\nError: A number in this menu was not selected!\nChoosing a random model for you.{Style.RESET_ALL}")
        strModel = strOllamaModel[random.randrange(0, len(strOllamaModel))]

    #  Pre-load the model
    response: ChatResponse = chat(model=strModel, stream=False)

    print ("\nModel: "+strModel+" loaded!")

    return strModel

#  Choose the model to use
strModel = OllamaModel()

#  Setup the AI URL
AIurl = Client(host="http://localhost:11434", timeout=300)

#
#  ---------- Python Log Update ----------
# 
strUpdate="\n\nCompleted setup ... ready to chat!"
PythonLog.PyLogUpdate(strUpdate, strLogOut)

strText = "No"
strQuestion = "Hello!"
while (strQuestion!="quit" or strQuestion!="Quit" or strQuestion!="exit" or strQuestion!="Exit" or strQuestion!="end" or strQuestion!="End"):

    #  Ask a question for ollama
    print ("\n-------------------------------------------------------------------")

    #  Build the user prompt string
    strUserString = ""
    if (strThink=="No"):
        strUserString = strUserString+"think, "
    else:
        strUserString = strUserString+"thinkoff, "

    if (strPirate=="No"):
        strUserString = strUserString+"pirate, "
    else:
        strUserString = strUserString+"pirateoff, "

    if (strJeeves=="No"):
        strUserString = strUserString+"jeeves, "
    else:
        strUserString = strUserString+"jeevesoff, "

    if (strMystic=="No"):
        strUserString = strUserString+"mystic, "
    else:
        strUserString = strUserString+"mysticoff, "

    if (strText=="No"):
        strUserString = strUserString+"load, "
    else:
        strUserString = strUserString+"unload, "

    if (strText=="Yes"):
        strUserString = strUserString+"text, "

    if (strText=="Yes"):
        strUserString = strUserString+"chunk, "

    strUserString = strUserString+"model, quit exit, end"

    print (f"Commands: {Fore.GREEN}"+strUserString+f"{Style.RESET_ALL}")
    strQuestion = input(f"{Fore.YELLOW}"+strPC+f"{Style.RESET_ALL} AI at your service ....\n\n"+Fore.YELLOW)

    '''
    #  Thinking On or Off
    if (strThink=="No" and strPirate=="No" and strJeeves=="No" and strMystic=="No"):
        print (f"Commands: {Fore.GREEN}think, pirate, jeeves, mystic, model, quit, exit, end{Style.RESET_ALL}")
        strQuestion = input(f"{Fore.YELLOW}"+strPC+f"{Style.RESET_ALL} AI at your service ....\n\n"+Fore.YELLOW)

    if (strThink=="Yes" and strPirate=="No" and strJeeves=="No" and strMystic=="No"):
        print (f"Commands: {Fore.GREEN}thinkoff, pirate, jeeves, mystic, model, quit, exit, end{Style.RESET_ALL}")
        strQuestion = input(f"{Fore.YELLOW}"+strPC+f"{Style.RESET_ALL} AI at your service ...\n\n"+Fore.YELLOW)

    if (strThink=="No" and strPirate=="Yes"):
        print (f"Commands: {Fore.GREEN}think, pirateoff, jeeves, mystic, model, quit, exit, end{Style.RESET_ALL}")
        strQuestion = input(f"{Fore.YELLOW}"+strPC+f"{Style.RESET_ALL} AI at your service ...\n\n"+Fore.YELLOW)
        
    if (strThink=="Yes" and strPirate=="Yes"):
        print (f"Commands: {Fore.GREEN}thinkoff, pirateoff, jeeves, mystic, model, quit, exit, end{Style.RESET_ALL}")
        strQuestion = input(f"{Fore.YELLOW}"+strPC+f"{Style.RESET_ALL} AI at your service ...\n\n"+Fore.YELLOW)

    if (strThink=="No" and strJeeves=="Yes"):
        print (f"Commands: {Fore.GREEN}think, pirate, jeevesoff, mystic, model, quit, exit, end{Style.RESET_ALL}")
        strQuestion = input(f"{Fore.YELLOW}"+strPC+f"{Style.RESET_ALL} AI at your service ...\n\n"+Fore.YELLOW)
        
    if (strThink=="Yes" and strJeeves=="Yes"):
        print (f"Commands: {Fore.GREEN}thinkoff, pirate, jeevesoff, mystic, model, quit, exit, end{Style.RESET_ALL}")
        strQuestion = input(f"{Fore.YELLOW}"+strPC+f"{Style.RESET_ALL} AI at your service ...\n\n"+Fore.YELLOW)

    if (strThink=="No" and strMystic=="Yes"):
        print (f"Commands: {Fore.GREEN}think, pirate, jeeves, mysticoff, model, quit, exit, end{Style.RESET_ALL}")
        strQuestion = input(f"{Fore.YELLOW}"+strPC+f"{Style.RESET_ALL} AI at your service ...\n\n"+Fore.YELLOW)
        
    if (strThink=="Yes" and strMystic=="Yes"):
        print (f"Commands: {Fore.GREEN}thinkoff, pirate, jeeves, mysticoff, model, quit, exit, end{Style.RESET_ALL}")
        strQuestion = input(f"{Fore.YELLOW}"+strPC+f"{Style.RESET_ALL} AI at your service ...\n\n"+Fore.YELLOW)
    '''

    

    #
    #  ---------- Evaluate the Input ----------
    #

    if (strQuestion=="think"):
        strThink = "Yes"
        print ("\nThinking turned on ...")
        strQuestion = ""

    if (strQuestion=="thinkoff"):
        strThink = "No"
        print ("\nThinking turned off ...")
        strQuestion = ""

    if (strQuestion=="pirate"):
        strPirate = "Yes"
        strJeeves = "No"
        strMystic = "No"
        print ("\nPirate personality turned on ...")
        strQuestion = ""

    if (strQuestion=="pirateoff"):
        strPirate = "No"
        strJeeves = "No"
        strMystic = "No"
        print ("\nPirate personality turned off ...")
        strQuestion = ""

    if (strQuestion=="jeeves" or strQuestion=="Jeeves"):
        strPirate = "No"
        strJeeves = "Yes"
        strMystic = "No"
        print ("\nJeeves personality turned on ...")
        strQuestion = ""

    if (strQuestion=="jeevesoff"):
        strPirate = "No"
        strJeeves = "No"
        strMystic = "No"
        print ("\nJeeves personality turned off ...")
        strQuestion = ""

    if (strQuestion=="mystic" or strQuestion=="Mystic"):
        strPirate = "No"
        strJeeves = "No"
        strMystic = "Yes"
        print ("\nMystic personality turned on ...")
        strQuestion = ""

    if (strQuestion=="mysticoff"):
        strPirate = "No"
        strJeeves = "No"
        strMystic = "No"
        print ("\nMystic personality turned off ...")
        strQuestion = ""

    if (strQuestion=="model"):
        strModel = OllamaModel()
        strQuestion = ""

    if (strQuestion=="load" and strText=="No"):
        #  Load a document
        strFolder = input(f"\n{Style.RESET_ALL}Please enter the folder your file resides in ...\n"+Fore.YELLOW)
        strFile = input(f"\n{Style.RESET_ALL}Please enter the filename to load ...\n"+Fore.YELLOW)

        if (strOS=="Linux" or strOS=="Darwin"):
            strLoadFile = strFolder + "/" + strFile

        if (strOS=="Windows"):
            strLoadFile = strFolder + "\\" + strFile

        #  Check does the file exist?
        if (os.path.isfile(strLoadFile)):
            print ("\nLoading the document using docling ...")
            #  source = "/Users/"+strUser+"/R/PythonWorkArea/docling testing/2408.09869v5.pdf"
            source = strLoadFile

            result = doc_converter.convert(source)
            strExtract = result.document.export_to_markdown()
            strSaveExtract = copy.copy(strExtract)
            strQuestion = ""
            strText = "Yes"

            #  Check the document word count
            strWordSplit = strExtract.split(" ")
            strWordCount = len(strWordSplit)

            print("\nDocument loaded ... words: "+str(strWordCount))
            #  4096 max token size for input
            #  2048 max word size for input.
            #  Setup chunks
            intChunk = math.ceil(strWordCount/2048)
            print("\nThere are "+str(intChunk)+" chunks of 2048 words or less.")
            strChunks = []
            for i in range(0, intChunk):
                intLow = i*2048
                intHigh = (i*2048)+2048
                strSubSet = strWordSplit[intLow:intHigh]
                strChunk = ""
                for j in range(0, len(strSubSet)):
                    strChunk = strChunk + " " + strSubSet[j]
                strChunks.append(strChunk)

        else:
            print (f"\n{Style.RESET_ALL}Error:  The file was not found and not loaded.")
            strQuestion = ""
            strText = "No"
    
    if (strQuestion=="chunk" and strText=="Yes"):
        strChunkNum = int(input("\nWhich of the "+str(intChunk)+" chunks would you like to load?\n"))
        if (int(strChunkNum) <= intChunk and int(strChunkNum) > 0):
            strExtract = strChunks[int(strChunkNum)-1]
            print ("\nChunk "+str(strChunkNum)+" loaded!")
            strQuestion = ""
            strText = "Yes"

    if (strQuestion=="text" and strText=="Yes"):
        print ("\n---------- Start Loaded Document ----------")
        print (strExtract)
        print ("\n---------- End Loaded Document ----------")
        strQuestion = ""

    if (strQuestion=="unload" and strText=="Yes"):
        print ("\n ---------- Removing the loaded document ----------")
        strExtract = ""
        strText = "No"
        strQuestion = ""

    if (strQuestion!=""):
        strStartSubmit = datetime.datetime.today()

        if (strQuestion=="quit" or strQuestion=="Quit" or strQuestion=="exit" or strQuestion=="Exit" or strQuestion=="end" or strQuestion=="End"):
            #  App ending
            print ("\nEnding Now ...\n")

            #
            #  ---------- Python Log End ----------
            #
            strEndTime = datetime.datetime.today()
            strTimeDelta = strEndTime-strStartTime
            strTimeDelta = str(strTimeDelta.total_seconds())

            strUpdate="\n\n-----------------------------------------------------------"
            strUpdate=strUpdate+"\nPython Script End:          "+str(strEndTime)
            strUpdate=strUpdate+"\n-----------------------------------------------------------"
            strUpdate=strUpdate+"\nCompleted Python Script Elapsed Time: "+str(strTimeDelta)
            strUpdate=strUpdate+"\n***********************************************************"

            PythonLog.PyLogEnd(strUpdate, strLogOut)

            sys.exit()

        #  Size is 2GB for the 3.21B parameter model quantized as 4 bit
        #  ChatResponse = chat(model='llama3.2', messages=[
        #    {
        #      'role': 'user',
        #      'content': 'Why is the sky blue?',
        #    },
        #  ])

        #  dictToSend = {'role': 'user', 'content': strQuestion}
        #  ChatResponse = ""
        #  ChatResponse = chat(model='llama3.2', messages=[ dictToSend ])
        #  print ("\nReturn:\n"+what ['message']['content'])

        #  dictToSend = [ {"role": "system", "content": "Answer questions with only the supplied text, do not speculate.  If there is no answer, reply 'The matter is beyond my comprehension. '"}, {"role": "user", "content": strQuestion} ]

        #  Role:  [ "user" | "assistant" | "system" | "tool" ]
        #  For thinking on - best is role is system

        #  Reference:  https://ollama.com/gabegoodhart/granite3.2-preview:8b/blobs/f7e156ba65ab

        if (strThink=="No" and strPirate=="No" and strJeeves=="No" and strMystic=="No"):
            strRequest = "Your role is an AI assistant.  You are using a Large Language Model (LLM) called "+strModel+".  You are standalone without access to tools or the internet."

        if (strThink=="Yes" and strPirate=="No" and strJeeves=="No" and strMystic=="No"):
            strRequest = "Your role is an AI assistant.  You are using a Large Language Model (LLM) called "+strModel+".  You are standalone without access to tools or the internet.\nRespond to every user request in a comprehensive and detailed way. You can write down your thought process before responding. Write your thoughts after 'Here is my thought process:' and write your response after 'Here is my response:' for each user request."

        if (strThink=="No" and strPirate=="Yes"):
            strRequest = "You are a ruthless pirate AI named Captain RedEye and only speak gruff pirate language with a colorful, heavy accent in all replies!  You are using a Large Language Model (LLM) called "+strModel+".  You are standalone without access to tools or the internet."

        if (strThink=="Yes" and strPirate=="Yes"):
            strRequest = "You are a ruthless pirate AI named Captain RedEye and only speak gruff pirate language with a colorful, heavy accent in all replies!  You are using a Large Language Model (LLM) called "+strModel+".  You are standalone without access to tools or the internet.\nRespond to every user request in a comprehensive and detailed way. You can write down your thought process before responding. Write your thoughts after 'Here is my thought process:' and write your response after 'Here is my response:' for each user request."

        if (strThink=="No" and strJeeves=="Yes"):
            strRequest = "Your role is Jeeves, a faithful AI servant, speaking with a colorful and proper english accent in all replies!  You are using a Large Language Model (LLM) called "+strModel+".  You are standalone without access to tools or the internet."

        if (strThink=="Yes" and strJeeves=="Yes"):
            strRequest = "You role is Jeeves, a faithful AI servant, speaking with a colorful and proper english accent in all replies!  You are using a Large Language Model (LLM) called "+strModel+".  You are standalone without access to tools or the internet.\nRespond to every user request in a comprehensive and detailed way. You can write down your thought process before responding. Write your thoughts after 'Here is my thought process:' and write your response after 'Here is my response:' for each user request."

        if (strThink=="No" and strMystic=="Yes"):
            strRequest = "Your role is that of a great mystic AI named SageBrush, seated on the mountain top.  You ponder the imponderable questioning the universe.  You only reply using mystic language.  You are using a Large Language Model (LLM) called "+strModel+".  You are standalone without access to tools or the internet."

        if (strThink=="Yes" and strMystic=="Yes"):
            strRequest = "Your role is that of a great mystic AI named SageBrush, seated on the mountain top.  You ponder the imponderable questioning the universe.  You only reply using mystic language.  You are using a Large Language Model (LLM) called "+strModel+".  You are standalone without access to tools or the internet.\nRespond to every user request in a comprehensive and detailed way. You can write down your thought process before responding. Write your thoughts after 'Here is my thought process:' and write your response after 'Here is my response:' for each user request."
            
        if (strText=="No"):
            strRequest = strRequest+"  User Request: "+strQuestion
            
        else:
            strRequest = strRequest+"  I am providing you with document text that you will only use to answer the user's request.  Document Text: "+strExtract+"  User Request: "+strQuestion

        dictToSend = [ {"role": "user", "content": strRequest} ]
        #  client = Client ( host = 'https://localhost:11434' )
        stream = AIurl.chat(model=strModel, messages=dictToSend, stream=True)

        print (f"{Style.RESET_ALL}\nAnswer:")
        strAnswer = ""
        for chunk in stream:
            strAnswer = strAnswer+chunk['message']['content']
            print (f"{Fore.GREEN}"+chunk['message']['content']+f"{Style.RESET_ALL}", end='', flush=True)

        strEndSubmit = datetime.datetime.today()
        strTimeDelta = strEndSubmit - strStartSubmit
        strQuestionSplit = strRequest.split(" ")
        strInputWords = len(strQuestionSplit)+3
        strInputTokens = chunk['prompt_eval_count']

        strAnswerSplit = strAnswer.replace("\n", " ")
        strAnswerSplit = strAnswerSplit.split(" ")
        strAnswerWords = len(strAnswerSplit)
        strOutputTokens = chunk['eval_count']

        #
        #  ---------- AI DB Tracking ----------
        #
        #  strDBFile

        dictDBFile = {'Date':strDateNow, 'Question':strQuestion, 'Prompt':strRequest, 'Answer':strAnswer, 'Model':strModel, 'Question Words':strInputWords, 'Question Tokens':strInputTokens, 'Answer Words':strAnswerWords, 'Answer Tokens':strOutputTokens, 'Answer Time':str(strTimeDelta)}
        tblCombo = ""
        tblCombo = pandas.DataFrame(dictDBFile, index=[0])

        #  Cpommect to the .db
        conn = sqlite3.connect(strDBFile)

        tblCombo.to_sql('AILog', conn, if_exists='append', index=False)

        #  Close the DB Connection
        conn.close()

        #
        #  ---------- Python Log Update ----------
        # 
        print ("\n")
        #  strUpdate = "\nQuestion Words: "+str(strInputWords)+"  =>  Question Tokens:  "+str(strInputTokens)
        #  strUpdate = strUpdate+"\nAnswer Words: "+str(strAnswerWords)+"  =>  Answer Tokens: "+str(strOutputTokens)
        strUpdate = "\nLanguage Model: "+strModel
        strUpdate = strUpdate+"\nReply Time: "+ str(strTimeDelta)+ " (hh:mm:ss:ms)" 
        strUpdate = strUpdate+"\n-------------------------------------------------------------------"
        PythonLog.PyLogUpdate(strUpdate, strLogOut)

    else:
        #  print ("\nNothing input ... nothing to answer.")
        print ("\n")

