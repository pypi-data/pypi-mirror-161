import click
import os

from colorama import Fore, init, Back,Style

import importlib.metadata
from directory_tree import display_tree

__version__ = importlib.metadata.version("ifood_ds_utils")
init()


@click.command()
def create_ifood_ds_template():
    os.system("cookiecutter https://github.com/javierjdaza/cookiecutter-ifood-DS.git")

@click.command()
def welcome_to_the_library():

    with open('./files/ascii-art.txt', 'r') as f:
        for line in f:
            click.echo(Fore.WHITE + line.rstrip())

@click.command()
@click.option('-dev', 'env_dev', is_flag=True, help='-dev <<s3://dev-ifood-ml-sagemaker/>>')
@click.option('-prd', 'env_prd', is_flag=True, help='-prd <<s3://prd-ifood-sagemaker-output-ohio/>>')
def upload_to_s3(env_dev,env_prd):
    click.echo(Fore.YELLOW + f"Don't forget to log in:{Fore.RED} ifood-aws-login")
    click.echo(Fore.YELLOW + "--"*25)
    tree_string_rep = display_tree(os.getcwd(), string_rep = True)

    click.echo(Fore.GREEN + tree_string_rep)
    current_folder = os.path.basename(os.getcwd())

    if env_dev:
        answer = click.prompt(f'{Fore.RED}This will be your folder tree that will be uploaded to S3,\nin the route: {Fore.YELLOW}s3://dev-ifood-ml-sagemaker/{current_folder}\n{Fore.RED}all right?\nyes/no' + Fore.WHITE + '\n')
        answer = answer.lower()
        if answer == 'yes' or answer == 'y':
            # click.echo("os.system(f'aws s3 cp s3://dev-ifood-ml-sagemaker/{current_folder}/ ./  --recursive')")
            os.system(f'aws s3 cp s3://dev-ifood-ml-sagemaker/{current_folder}/ ./  --recursive')
    else:
        answer = click.prompt(f'{Fore.RED}This will be your folder tree that will be uploaded to S3,\nin the route: {Fore.YELLOW}s3://prd-ifood-sagemaker-output-ohio/{current_folder}\n{Fore.RED}all right?\nyes/no' + Fore.WHITE + '\n')
        answer = answer.lower()
        if answer == 'no' or answer == 'n':
            # click.echo("os.system(f'aws s3 cp s3://prd-ifood-sagemaker-output-ohio/{current_folder}/ ./  --recursive')")
            os.system(f'aws s3 cp s3://prd-ifood-sagemaker-output-ohio/{current_folder}/ ./  --recursive')

@click.command()
@click.option('-version','-V', 'version', is_flag=True, help='--v: Display Version of the package')
def version(version:str):
    """

    This package is for speed up some aws cli commands

    \b
    @command: upload-folder-s3 -> [Upload your current work directory in S3] 
        @options: -dev or -prd
    @command: template ->[Create the ifood DS template ]

    
    """
    if version:
        click.echo(Fore.GREEN + f'ifood-ds-utils version: {__version__}')
    else:
   
        click.echo(
            """
****************************************************************************************************
****************************************************************************************************
****************************************************************************************************
***************************#@@@&****@@@@@@*******************************@@@@***********************
*********************************(@@@************************************@@@@***********************
**************************%@@@&@@@@@@@@@**@@@@@@@@****(@@@@@@@(****@@@@@@@@@************************
**************************@@@@**@@@@***@@@@@@@@@@@@*@@@@@@@@@@@&*@@@@@@@@@@@************************
*************************#@@@%**@@@@**@@@@@@@@@@@@*@@@@@@@@@@@@*@@@@@@@@@@@*************************
*************************@@@@**@@@@***@@@@@@@@@@@**@@@@@@@@@@@*@@@@@@@@@@@@*************************
************************%@@@&**@@@@*****&@@@@(*******@@@@@******@@@@**@@@@**************************
******************************@@@@******************************************************************
*************************************@*****************@@@@@****************************************
**************************************@@(***********@@@@@@@@****************************************
*****************************************@@@@@@@@@@@@@@@**@*****************************************
****************************************************************************************************
****************************************************************************************************
****************************************************************************************************
            """)
        # help()


@click.command()
def help():
    """ifood-ds-utils

    This package is for speed up some aws cli commands

    \b
    upload-folder-s3 [Upload your current work directory in S3] params: -dev or -prd
    template [Create the ifood DS template ]

    
    """