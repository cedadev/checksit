import json
from os.path import exists


####################
# USEFUL FUNCTIONS #
####################

def map_data_type(dtype):
    data_map = {
        'float64':'double',
        'float32':'float',
        'int32':'int',
        'byte':'byte',
    }
    return data_map[dtype]
    
    

# main function

def make_amof_specs(version_number): 
    ###############
    # DIRECTORIES #
    ###############
    
    cvs_dir = f"./checksit/vocabs/AMF_CVs/{version_number}"
    out_dir = f"./specs/groups/ncas-amof-{version_number}"


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
            if r'YYYY-MM-DDThh:mm:ss\.\d+ _or_ N/A' in compliance:
                rule = "regex-rule:datetime-or-na"
            elif 'vN.M' in compliance:
                rule = "regex-rule:match:vN.M"
            elif r'YYYY-MM-DDThh:mm:ss\.\d+' in compliance:
                rule = "regex-rule:datetime"
            elif '<number> m' in compliance:
                rule = r"regex:^-?\d+\.?\d* m$"
            else:
                rule = f"regex-rule:EDIT:{compliance}"
        elif compliance.lower() in ["number","integer","int","float","string","str"]:
            rule = f"type-rule:{compliance.lower()}"
        elif compliance.lower() == "exact match in vocabulary":
            # known vocab matches
            if attr == 'source':
                rule = (f"__vocabs__:AMF_CVs/{version_number}/AMF_ncas_instrument:"
                        "ncas_instrument:__all__:description")
            elif attr == 'platform':
                rule = f"__vocabs__:AMF_CVs/{version_number}/AMF_platform:platform:__all__"
            else:
                # a few extra catches
                if attr == "institution":
                    rule = "regex:National Centre for Atmospheric Science (NCAS)"
                elif attr == "platform_type":
                    rule = "rule-func:match-one-of:stationary_platform|moving_platform"
                elif attr == "featureType":
                    rule = "rule-func:match-one-of:timeSeries|timeSeriesProfile|trajectory"
                else:
                    rule = f"__vocabs__:EDIT:{compliance}"
        elif "one of: " in compliance.lower():
            options = compliance.split(': ')[1]
            options = options.replace(',','|')
            while ' ' in options:
                options = options.replace(' ','')
            rule = f"rule-func:match-one-of:{options}"
        else:
            rule = f"UNKNOWN compliance: {compliance}"
        rule = rule.replace('(',r'\(')
        rule = rule.replace(')',r'\)')
        rule = [ rule.replace(' ',r'\s') if "regex:" in rule else rule ][0]
        attr_rules[attr] = rule


    with open(f'{out_dir}/amof-global-attrs.yml', 'w') as f:
        f.write(('required-global-attrs:\n  func: checksit.generic.check_global_attrs\n'
                 '  params:\n    vocab_attrs:\n'))
        for attr, rule in attr_rules.items():
            if "__vocabs__" in rule:
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
            #deploy_vars_attrs = {}
            deploy_vars = {}
            for variable in data.keys():
                deploy_vars[variable] = []
                for attr in data[variable].keys():
                    attr_value = data[variable][attr]
                    if attr == 'type':
                        attr_value = map_data_type(attr_value)
                    deploy_vars[variable].append(f'{attr}:{attr_value}')
         


        spec_file_name = f'{out_dir}/amof-common-{mode}.yml'
        with open(spec_file_name, 'w') as f:
            # variables
            for i, var in enumerate(deploy_vars.items()):
                f.write(f'var-requires{i}:\n')
                f.write(('  func: checksit.generic.check_var\n  params:\n    variable:\n'
                         f'      - {var[0]}\n    defined_attrs:\n'))
                for attr in var[1]:
                    attr_key = attr.split(':')[0]
                    attr_value = ':'.join(attr.split(':')[1:])
                    f.write(f'      - {attr_key}:{attr_value}\n')
            f.write('\n')
            # dimensions
            f.write(('dims-requires:\n  func: checksit.generic.check_dim_exists\n'
                     '  params:\n    dimensions:\n'))
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
                product_info = {}
                for variable in data.keys():
                    product_info[variable] = []
                    for attr in data[variable].keys():
                        attr_value = data[variable][attr]
                        if attr == 'flag_meanings':
                            attr_value = attr_value.replace('|',' ').replace('  ',' ')
                        elif attr == 'type':
                            attr_value = map_data_type(attr_value)
                        product_info[variable].append(f'{attr}:{attr_value}')
            prod_vars_exist = True
        else:
            prod_vars_exist = False

        if exists(f'{cvs_dir}/AMF_product_{product}_dimension.json'):
            with open(f'{cvs_dir}/AMF_product_{product}_dimension.json') as f:
                product_dims = json.load(f)[f'product_{product}_dimension'].keys()
            prod_dims_exist = True
        else:
            prod_dims_exist = False

    
        if exists(f'{cvs_dir}/AMF_product_{product}_global-attributes.json'):
            with open(f'{cvs_dir}/AMF_product_{product}_global-attributes.json') as f:
                data = json.load(f)[f'product_{product}_global-attributes']
            
                attr_rules = {}

                for attr in data.keys():
                    compliance = data[attr]['compliance_checking_rules']
                    if compliance.lower() in ["exact match",
                                              "exact match of text to the left"]:
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
                        if r'YYYY-MM-DDThh:mm:ss\.\d+ _or_ N/A' in compliance:
                            rule = "regex-rule:datetime-or-na"
                        elif 'vN.M' in compliance:
                            rule = "regex-rule:match:vN.M"
                        elif r'YYYY-MM-DDThh:mm:ss\.\d+' in compliance:
                            rule = "regex-rule:datetime"
                        else:
                            rule = f"regex-rule:EDIT:{compliance}"
                    elif compliance.lower() in ["number","integer",
                                                "int","float","string","str"]:
                        rule = f"type-rule:{compliance.lower()}"
                    elif compliance.lower() == "exact match in vocabulary":
                        if attr == 'source':
                            rule = ("__vocabs__:AMF_CVs/AMF_ncas_instrument:"
                                    "ncas_instrument:__all__:description")
                        elif attr == 'platform':
                            rule = "__vocabs__:AMF_CVs/AMF_platform:platform:__all__"
                        else:
                            rule = f"__vocabs__:EDIT:{compliance}"
                    elif "one of: " in compliance.lower():
                        options = compliance.split(': ')[1]
                        options = options.replace(',','|')
                        while ' ' in options:
                            options = options.replace(' ','')
                        rule = f"rule-func:match-one-of:{options}"
                    else:
                        rule = f"UNKNOWN compliance: {compliance}"
                    rule = rule.replace('(',r'\(')
                    rule = rule.replace(')',r'\)')
                    rule = [ rule.replace(' ',r'\s') if "regex:" in rule else rule ][0]
                    attr_rules[attr] = rule
            prod_attrs_exist = True
        else:
            prod_attrs_exist = False

        

        spec_file_name = f'{out_dir}/amof-{product}.yml'
        with open(spec_file_name, 'w') as f:
            if prod_vars_exist:
                for i, var in enumerate(product_info.items()):
                    f.write(f'var-requires{i}:\n')
                    f.write(('  func: checksit.generic.check_var\n'
                             '  params:\n    variable:\n'
                             f'      - {var[0]}:__OPTIONAL__\n    defined_attrs:\n'))
                    for attr in var[1]:
                        attr_key = attr.split(':')[0]
                        attr_value = ':'.join(attr.split(':')[1:])
                        f.write(f'      - {attr_key}:{attr_value}\n')
    
            if prod_dims_exist:
                f.write(('dims-requires:\n  func: checksit.generic.check_dim_exists\n'
                         '  params:\n    dimensions:\n'))
                for dim in product_dims:
                    f.write(f'      - {dim}:__OPTIONAL__\n')
            if prod_attrs_exist:
                f.write(('\nrequired-global-attrs:\n  func:'
                         ' checksit.generic.check_global_attrs\n'
                         '  params:\n    vocab_attrs:\n'))
                for attr, rule in attr_rules.items():
                    if "__vocabs__" in rule:
                        f.write(f'      {attr}: {rule}\n')
                f.write('    rules_attrs:\n')
                for attr, rule in attr_rules.items():
                    if rule.split(':')[0] in ['regex','regex-rule','type-rule','rule-func']:
                        f.write(f'      {attr}: {rule}\n') 


if __name__ == "__main__":
    import sys
    version_number = sys.argv[1]
    make_amof_specs(version_number) 
