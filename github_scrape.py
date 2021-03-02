import requests
import json
import time
import sys
import traceback
import time
from tqdm import tqdm

def get_repos(page_count, page_size, query, filter_lang, file_filter, out_path, get_func):
    repo_count = 0
    used_repos = 0
    file_count = 0
    files_checked = 0
    with open(out_path, 'a') as out_f:
        for pc in tqdm(range(page_count)):
            base_url = f'https://api.github.com/search/repositories?q={query}&page={pc+1}&per_page={page_size}'
            dat = get_func(base_url).json()
            # filter to only specific lang
            if 'items' in dat.keys():
                for rep in dat['items']:
                    if (rep['language'] == filter_lang):
                        try:
                            matching_files, checked = get_all_matching_files(
                                rep['contents_url'][:-8], file_filter, get_func)
                            files_checked += checked
                            if len(matching_files) > 0:
                                rep['matching_files'] = matching_files
                                out_f.write(json.dumps(rep) + '\n')
                                file_count += len(rep['matching_files'])
                                used_repos += 1
                        except Exception:
                            traceback.print_exc()
                    repo_count += 1
            else:
                print(dat)
            if (pc % 5 == 0):
                tqdm.write(f'{repo_count} {filter_lang} "{query}" repos checked, {file_count} files matching "{file_filter}" in {used_repos} repos. {files_checked} total files checked')

def get_all_matching_files(path, file_filter, get_func):
    matching_files = []
    files_checked = 0
    dat = get_func(path).json()
    for f in dat:
        if isinstance(f, str):
            print(f'{path} produced {dat} \n \n with f: {f}')
            continue
        fname = f['name']
        if f['type'] == 'dir':
            matches, checked = get_all_matching_files(f'{path}/{fname}', file_filter, get_func)
            matching_files.extend(matches)
            files_checked += checked
        else:
            if any([fname.endswith(fl) for fl in file_filter]):
                f_text = get_func(f['download_url']).text
                matching_files.append({'path': f['path'], 'contents': f_text})
            files_checked += 1
    return matching_files, files_checked

def limited_get(url, wait_time, user, toke):
    resp = requests.get(url, auth=(user,toke))
    if 'application/json' in resp.headers.get('content-type'):
        respj = resp.json()
        if not isinstance(respj, list) and 'message' in respj.keys() and 'API rate limit exceeded' in respj['message']:
            print(f'Rate limited. waiting for {wait_time} seconds')
            time.sleep(wait_time)
            return limited_get(url, user, toke)
    return resp

if __name__ == '__main__':
    toke = sys.argv[1]
    get_func = lambda url: limited_get(url, 120, 'PWhiddy', toke)
    get_repos(20000, 5, 'shader', 'GLSL', ['.glsl','.frag'], 'list_github_shader_files.jsonl', get_func)
