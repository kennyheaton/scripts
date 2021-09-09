import argparse
import yaml
import copy
import io

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--dev")
parser.add_argument("-q", "--qa")
parser.add_argument("-s", "--stage")
parser.add_argument("-p", "--prod")


args = vars(parser.parse_args())

manifest = {
    'applications': [
        {
            'name': '((name))',
            'buildpacks': [
                'https://github.com/mendix/cf-mendix-buildpack'
            ],
            'disk_quota': '((disk_quota))',
            'env': {},
            'instances': '((instances))',
            'memory': '((memory))',
            'routes': [
                {
                    'route': '((name)).cfapps.us10.hana.ondemand.com'
                }
            ],
            'services': [
                '((service1))',
                '((service2))',
                '((service3))',
                '((service4))',
                '((service5))',
                '((service6))',
                '((service7))',
            ],
            'stack': 'cflinuxfs3',
            'timeout': 180
        }
    ]
}

var_file = {
    'name': '',
    'disk_quota': '',
    'instances': '',
    'memory': '',
    'service1': '',
    'service2': '',
    'service3': '',
    'service4': '',
    'service5': '',
    'service6': '',
    'service7': '',
}

secret = {}

env_vars = {}

for env in ["dev", "qa", "stage", "prod"]:
    if args[env]:
        with open(args[env], 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            app = data_loaded['applications'][0]
            for key in app['env']:
                env_vars[key] = True


for env in ["dev", "qa", "stage", "prod"]:
    if args[env]:
        with open(args[env], 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            app = data_loaded['applications'][0]
            var = copy.deepcopy(var_file)
            secret_var = copy.deepcopy(secret)
            var['name'] = app['name']
            var['disk_quota'] = app['disk_quota']
            var['instances'] = app['instances']
            var['memory'] = app['memory']
            for index in range(len(app['services'])):
                var['service' + str(index + 1)] = app['services'][index]
            for key in env_vars:
                if key in app['env']:
                    hide = 'key' in key.lower() \
                           or 'secret' in key.lower() \
                           or 'password' in key.lower() \
                           or 'pass' in key.lower() \
                           or 'sec' in key.lower()
                    if hide:
                        secret_var[key.lower()] = app['env'][key]
                    else:
                        var[key.lower()] = app['env'][key]
                else:
                    var[key.lower()] = ''
                manifest['applications'][0]['env'][key] = '(({}))'.format(key.lower())
            with io.open('{}.yml'.format(env), 'w', encoding='utf8') as outfile:
                yaml.dump(var, outfile, default_flow_style=False, allow_unicode=True)
            with io.open('{}-secret.yml'.format(env), 'w', encoding='utf8') as outfile:
                yaml.dump(secret_var, outfile, default_flow_style=False, allow_unicode=True)

with io.open('manifest.yml', 'w', encoding='utf8') as outfile:
    yaml.dump(manifest, outfile, default_flow_style=False, allow_unicode=True)
