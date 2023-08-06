import os
import sys


import boto3
from jinja2 import Environment, meta

client = boto3.client('ssm',region_name='sa-east-1')
main_dir = os.path.dirname(str(sys.modules['__main__'].__file__))

def process(operation, provider):

    extensions = []
    env = None
    if operation == 'build':
        extensions.append('.prebuild')
        extensions.append('.preall')
        env = Environment(
        block_start_string='<%',
        block_end_string= '%>',
        variable_start_string= '<<%',
        variable_end_string='%>>',
        comment_start_string='<#',
        comment_end_string='#>'
        )
    elif operation == 'deploy':
        extensions.append('.predeploy')
        env = Environment(
        block_start_string='<$%',
        block_end_string= '%$>',
        variable_start_string= '<<$%',
        variable_end_string='%$>>',
        comment_start_string='<$#',
        comment_end_string='#$>'
        )

    renderer = getRenderer(operation)

    files = findFilesWithExtensions(extensions)

    print(files)

    toRender = []
    
    for file in files:
        with open(file) as f:
            content = f.read()
            template = env.from_string(content)
            toRender.append({"file": file, "template": template, "variables": meta.find_undeclared_variables(env.parse(content))}) 

    variables = set()
    for cosa in toRender:
        variables.update(cosa['variables'])  
    
    getParameters = getProvider(provider)

    values = getParameters(variables)

    renderer(toRender, values)



def findFilesWithExtensions(extensions):
    files = []
    
    exclude = set(['node_modules'])
    for root, dirnames, filenames in os.walk(main_dir):
        dirnames[:] = [d for d in dirnames if d not in exclude]
        for file in filenames:
            print()
            fname, fext = os.path.splitext(file)
            if fext in extensions:  #and myStr in fname
                files.append(os.path.join(root, file))

    return files



def getFileParameters(names):
    values = {}
    with open(os.path.join(main_dir, 'parameters-file.preprocess')) as f:
        for line in f:
            lineValue = line.rstrip()
            if lineValue is not None:
                a = lineValue.split('=')
                if a[0] in names:
                    name = a[0]
                    value = a[1]
                    values.update({f'{name}': value})

    return values

def getSSMParameters(names):
    values={}
    response = client.get_parameters(Names=list(names), WithDecryption=False)
    print(response)
    for p in response['Parameters']:
        values.update({f"{p['Name']}": p['Value']})

    print(values)
    return values

def getProvider(provider):
    options = {
        'file': getFileParameters,
        'ssm': getSSMParameters,
    }
    return options[provider]

def BuildRenderer(toRender, values):
    for render in toRender:
        fname, fext = os.path.splitext(render['file'])
        finalSufix = ''
        if fext == '.preall':
            finalSufix = '.predeploy'
        with open(f'{fname}{finalSufix}', 'w') as file:
            file.write(render['template'].render(values))
        os.remove(render['file'])


def DeployRenderer(toRender, values):
    for render in toRender:
        fname, fext = os.path.splitext(render['file'])
        with open(f'{fname}', 'w') as file:
            file.write(render['template'].render(values))
        os.remove(render['file'])

def getRenderer(operation):
    options = {
        'build': BuildRenderer,
        'deploy': DeployRenderer,
    }
    return options[operation]