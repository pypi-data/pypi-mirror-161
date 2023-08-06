import os
import sys
import getopt


import boto3
from jinja2 import Environment, meta

# import requests
dir_path = os.path.dirname(os.path.realpath(__file__))

client = boto3.client('ssm',region_name='sa-east-1')


def process(operation, provider):
    # operation = None
    # provider = None
    # try:
    #     opts, args = getopt.getopt(argv,"ho:p:",["operation=","provider="])
    # except getopt.GetoptError:
    #     sys.exit(2)
    # for opt, arg in opts:
    #     if opt == '-h':
    #         sys.exit()
    #     elif opt in ("-o", "--operation"):
    #         operation = arg
    #     elif opt in ("-p", "--provider"):
    #         provider = arg

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
    for root, dirnames, filenames in os.walk(dir_path):
        dirnames[:] = [d for d in dirnames if d not in exclude]
        for file in filenames:
            fname, fext = os.path.splitext(file)
            if fext in extensions:  #and myStr in fname
                files.append(os.path.join(root, file))

    return files



def getFileParameters(names):
    dir = os.path.dirname(str(sys.modules['__main__'].__file__))
    values = {}
    with open(os.path.join(dir, 'parameters-file.preprocess')) as f:
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

if __name__ == "__main__":
    main(sys.argv[1:])