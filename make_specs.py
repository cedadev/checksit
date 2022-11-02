import json
from os.path import exists




###############
# DIRECTORIES #
###############

cvs_dir = "./checksit/vocabs/AMF_CVs"
out_dir = "./specs/groups"



################
# GLOBAL ATTRS #
################

with open(f'{cvs_dir}/AMF_product_common_global-attributes_land.json') as f:
    data = json.load(f)['product_common_global-attributes_land']

attr_rules = {}

for attr in data.keys():
    compliance = data[attr]['compliance_checking_rules']
    if compliance.lower() in ["exact match", "exact match of text to the left"]:
        rule = f"regex:{data[attr]['fixed_value']}"
    elif "String: min" in compliance:
        number = compliance.split(' ')[2]
        rule = f"rule-func:string-of-length:{number}+"
    elif compliance.lower() == "valid email":
        rule = "regex-rule:valid-email"
    elif compliance.lower() == "valid url":
        rule = "regex-rule:valid-url"
    elif compliance.lower() == "valid url _or_ n/a":
        rule = "regex-rule:valid-url-or-na"
    elif "match: " in compliance.lower():
        rule = f"regex-rule:EDIT:{compliance}"
    elif compliance.lower() in ["number","integer","int","float","string","str"]:
        rule = f"type-rule:{compliance.lower()}"
    elif compliance.lower() == "exact match in vocabulary":
        rule = f"__vocab__:EDIT:{compliance}"
    elif "one of: " in compliance.lower():
        options = compliance.split(': ')[1]
        options = options.replace(',','|')
        while ' ' in options:
            options = options.replace(' ','')
        rule = f"rule-func:match-one-of:{options}"
    else:
        rule = f"UNKNOWN compliance: {compliance}"
    rule = rule.replace('(','\(')
    rule = rule.replace(')','\)')
    rule = rule.replace(' ','\s')
    attr_rules[attr] = rule


with open(f'{out_dir}/amof-global-attrs.yml', 'w') as f:
    f.write('required-global-attrs:\n  func: checksit.generic.check_global_attrs\n  params:\n    vocab_attrs:\n')
    for attr, rule in attr_rules.items():
        if "__vocab__" in rule:
            f.write(f'      {attr}: {rule}\n')
    f.write('    rules_attrs:\n')
    for attr, rule in attr_rules.items():
        if rule.split(':')[0] in ['regex','regex-rule','type-rule','rule-func']:
            f.write(f'      {attr}: {rule}\n') 



####################
# DEPLOYMENT MODES #
####################

deployment_modes = ['land','sea','air','trajectory']

for mode in deployment_modes:
    with open(f'{cvs_dir}/AMF_product_common_dimension_{mode}.json') as f:
        deploy_dims = json.load(f)[f'product_common_dimension_{mode}'].keys()
    with open(f'{cvs_dir}/AMF_product_common_variable_{mode}.json') as f:
        data = json.load(f)[f'product_common_variable_{mode}']
        deploy_vars_attrs = {}
        deploy_vars = {}
        count = 0
        for variable in data.keys():
            attrs = data[variable].keys()
            if attrs not in deploy_vars_attrs.values():
                deploy_vars_attrs[count] = attrs
                deploy_vars[count] = [variable]
                count += 1
            else:
                # find key based on value
                for attr_key in deploy_vars_attrs.keys():
                    if deploy_vars_attrs[attr_key] == attrs:
                        deploy_vars[attr_key].append(variable)
     


    spec_file_name = f'{out_dir}/amof-common-{mode}.yml'
    with open(spec_file_name, 'w') as f:
        # variables
        for key_number in deploy_vars.keys():
            f.write(f'var-requires{key_number}:\n')
            f.write('  func: checksit.generic.check_var\n  params:\n    variables:\n')
            for var in deploy_vars[key_number]:
                f.write(f'      - {var}\n')
            f.write('    defined_attrs:\n')
            for attr in deploy_vars_attrs[key_number]:
                f.write(f'      - {attr}\n')
        f.write('\n')
        # dimensions
        f.write('dims-requires:\n  func: checksit.generic.check_dim_exists\n  params:\n    dimensions:\n')
        for dim in deploy_dims:
            f.write(f'      - {dim}\n')





##############
## PRODUCTS ##
##############

# load all products
with open(f'{cvs_dir}/AMF_product.json') as f:
    products = json.load(f)['product']


# go through each product, create spec file
for product in products:
    product = product.replace(' ','')

    if exists(f'{cvs_dir}/AMF_product_{product}_variable.json'):
        with open(f'{cvs_dir}/AMF_product_{product}_variable.json') as f:
            data = json.load(f)[f'product_{product}_variable']
            product_attrs_info = {}
            count = 0
            product_info = {}
            for variable in data.keys():
                attrs = data[variable].keys()
                if attrs not in product_attrs_info.values():
                    product_attrs_info[count] = attrs
                    product_info[count] = [variable]
                    count += 1
                else:
                    # find key based on value
                    for attr_key in product_attrs_info.keys():
                        if product_attrs_info[attr_key] == attrs:
                            product_info[attr_key].append(variable)
        prod_vars_exist = True
    else:
        prod_vars_exist = False

    if exists(f'{cvs_dir}/AMF_product_{product}_dimension.json'):
        with open(f'{cvs_dir}/AMF_product_{product}_dimension.json') as f:
            product_dims = json.load(f)[f'product_{product}_dimension'].keys()
        prod_dims_exist = True
    else:
        prod_dims_exist = False


    spec_file_name = f'{out_dir}/amof-{product}.yml'
    with open(spec_file_name, 'w') as f:
        if prod_vars_exist:
            for key_number in product_info.keys():
                f.write(f'var-requires{key_number}:\n')
                f.write('  func: checksit.generic.check_var\n  params:\n    variables:\n')
                for var in product_info[key_number]:
                    f.write(f'      - {var}\n')
                f.write('    defined_attrs:\n')
                for attr in product_attrs_info[key_number]:
                    f.write(f'      - {attr}\n')
            f.write('\n')
        if prod_dims_exist:
            f.write('dims-requires:\n  func: checksit.generic.check_dim_exists\n  params:\n    dimensions:\n')
            for dim in product_dims:
                f.write(f'      - {dim}\n')
            
