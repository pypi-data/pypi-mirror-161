import argparse
import datetime
import json
import logging
import os
import sys
import http.client

from ws_import_spdx._version import __version__, __tool_name__

logger = logging.getLogger(__tool_name__)
logger.setLevel(logging.DEBUG)
is_debug = logging.DEBUG if bool(os.environ.get("DEBUG", 0)) else logging.INFO

formatter = logging.Formatter('%(levelname)s %(asctime)s %(thread)d %(name)s: %(message)s')
s_handler = logging.StreamHandler()
s_handler.setFormatter(formatter)
s_handler.setLevel(is_debug)
logger.addHandler(s_handler)
logger.propagate = False


def parse_args():
    parser = argparse.ArgumentParser(description='Utility to load SBOM report to Mend')
    parser.add_argument('-u', '--userKey', help="WS User Key", dest='ws_user_key', default=os.environ.get("WS_USER_KEY"), required=True if not os.environ.get("WS_USER_KEY") else False)
    parser.add_argument('-k', '--token', help="WS Key", dest='ws_token', default=os.environ.get("WS_TOKEN"), required=True if not os.environ.get("WS_TOKEN") else False)
    parser.add_argument('-s', '--scope', help="Project token for updating ", dest='scope_token', default=os.environ.get("WS_SCOPE_TOKEN"))
    parser.add_argument('-p', '--project', help="WS PROJECT NAME", dest='ws_project', default=os.environ.get("WS_PROJECT_NAME", ''))
    parser.add_argument('-pr', '--product', help="WS PRODUCT Token", dest='ws_product', required=True, default=os.environ.get("WS_PRODUCT_TOKEN", ''))
    parser.add_argument('-sbom', '--sbom', help="SBOM Report for upload", dest='sbom', required=True, default=os.environ.get("SBOM", ''))
    parser.add_argument('-t', '--updatetype', help="Update type", dest='update_type', default=os.environ.get("UPDATE_TYPE", 'OVERRIDE'))
    parser.add_argument('-o', '--out', help="Output directory", dest='out_dir', default=os.getcwd())
    parser.add_argument('-a', '--wsUrl', help="WS URL", dest='ws_url', default=os.environ.get("WS_URL", 'saas'))
    parser.add_argument('-l', '--load', help="Load to Mend", dest='load', default=True)
    arguments = parser.parse_args()

    return arguments


def check_el_inlist(name : str) -> bool:
    res = False
    for rel in relations:
        for key, value in rel.items():
            if 'SPDXRef-PACKAGE-'+name == value:
                res = True
                break
    return res


def get_element_by_spdxid(spdx : str) -> dict:
    out_el = {}
    for el in pkgs:
        if el['SPDXID'] == spdx:
            try:
                sha1 = f"{el['checksums'][0]['checksumValue']}"
            except:
                sha1 = ''
            try:
                chld = el['children']
            except:
                chld = []
            out_el = {
                "artifactId": f"{el['packageFileName']}",
                "version": f"{el['versionInfo']}",
                "sha1": sha1,
                "systemPath": "",
                "optional": False,
                "filename": f"{el['packageFileName']}",
                "checksums": {
                    "SHA1": sha1
                },
                "dependencyFile": "",
                "children" : chld
            }
            break
    return out_el


def add_child(element : dict) -> dict:  #recursion for adding childs
    new_el = element
    name = element['artifactId']
    for rel in relations:
        for key, value in rel.items():
            if key == 'SPDXRef-PACKAGE-'+name:
                chld_el = get_element_by_spdxid(value)
                try:
                    new_el['children'].append(chld_el)
                except:
                    new_el['children'] = [chld_el]
                added_el.append(chld_el['artifactId'])
                add_child(chld_el)
    return new_el


def create_body(args):
    ts = round(datetime.datetime.now().timestamp())
    global relations
    global pkgs
    global added_el
    relations = []
    added_el = []
    dep = []

    try:
        f = open(args.sbom,"r")
        sbom = json.load(f)
    except Exception as err:
        logger.error(f"Error opening SBOM file: {err}")
        exit(-1)

    for rel in sbom['relationships']:
        if rel['relationshipType'] == "DEPENDS_ON":
            relations.append({rel['spdxElementId'] : rel['relatedSpdxElement']})

    pkgs = sbom['packages']
    for package in pkgs:
        try:
            sha1 = f"{package['checksums'][0]['checksumValue']}"
        except:
            sha1 = ''

        pck = {
            "artifactId": f"{package['packageFileName']}",
            "version": f"{package['versionInfo']}",
            "sha1": sha1,
            "systemPath": "",
            "optional": False,
            "filename": f"{package['packageFileName']}",
            "checksums": {
                "SHA1": sha1
            },
            "dependencyFile": ""
        }
        if not check_el_inlist(package['packageFileName']):
            added_el.append(f"{package['packageFileName']}")   #we add element to list if was not added before
            dep.append(add_child(pck))

    if args.scope_token == '' or args.scope_token is None:
        if args.ws_project == '' :
            logger.error("Project name or project token should be defined")
            exit(-1)

        prj = [
            {
                "coordinates": {
                    "artifactId": f"{args.ws_project}"
                },
                "dependencies": dep
            }
        ]
    else:
        prj = [
            {
                "dependencies": dep,
                "projectToken": f"{args.scope_token}"
            }
        ]

    out = {
        "updateType": f"{args.update_type}",
        "type": "UPDATE",
        "agent": "fs-agent",
        "agentVersion": "",
        "pluginVersion": "",
        "orgToken": f"{args.ws_token}",
        "userKey": f"{args.ws_user_key}",
        "product": f"{args.ws_product}",
        "productVersion": "",
        "timeStamp": ts,
        "projects": prj
    }
    return out


def upload_to_mend(upload):
    ts = round(datetime.datetime.now().timestamp())
    try:
        conn = http.client.HTTPSConnection(f"{args.ws_url}.whitesourcesoftware.com")
        payload = f"type=UPDATE&updateType={args.update_type}&agent=fs-agent&agentVersion=1.0&token={args.ws_token}&" \
                  f"userKey={args.ws_user_key}&product={args.ws_product}&timeStamp={ts}&diff={upload['projects']}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        conn.request("POST", "/agent", payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read())
        if data['status'] == 1:
            logger.info("Data was updated/created successfully")
        else:
            logger.error(f"Error during upload data to Mend: {data['message']}")
        conn.close()
    except Exception as err:
        logger.error(f"Error during upload data to Mend: {err}")


def main():
    global output_json
    global args
    output_json = {}
    try:
        args = parse_args()
        if not os.path.exists(args.out_dir):
            logger.info(f"Dir: {args.out_dir} does not exist. Creating it")
            os.mkdir(args.out_dir)
        full_path = os.path.join(args.out_dir, f"Mend_upload_{datetime.datetime.now().strftime('%Y%m%d')}.json")

        output_json = create_body(args)
        if args.load:
            upload_to_mend(output_json)

        with open(full_path, 'w') as outfile:
            json.dump(output_json, outfile, indent=4)
    except Exception as err:
        logger.error(f"Error creating upload file: {err}")


if __name__ == '__main__':
    sys.exit(main())
