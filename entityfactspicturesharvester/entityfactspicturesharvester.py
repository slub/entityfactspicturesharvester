#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import json
import os
import socket
import sys
from threading import current_thread

import requests
import rx
from rx import operators as op
from rx.scheduler import ThreadPoolScheduler

# import time

USER_AGENT_HTTP_HEADER_KEY = 'user-agent'
# to respect User Agent policy for Wikimedia sites, see https://meta.wikimedia.org/wiki/User-Agent_policy
USER_AGENT_PATTERN = "entityfactspicturesharvester-bot-from-{0}/0.0.1 (https://github.com/slub/entityfactspicturesharvester; zazi@smiy.org) entityfactspicturesharvester/0.0.1"
SLASH = "/"
DOT = "."
QUESTION_MARK = "?"
ID_IDENTIFIER = "@id"
DEPICTION_IDENTIFIER = "depiction"
THUMBNAIL_IDENTIFIER = "thumbnail"
IMAGE_PREFIX = "image_"
THUMBNAIL_PREFIX = "thumbnail_"

PICTURE_CONTENT_TYPE = "picture"
THUMBNAIL_CONTENT_TYPE = "thumbnail"

PICTURE_THREAD_POOL_SCHEDULER = ThreadPoolScheduler(2)
THUMBNAIL_THREAD_POOL_SCHEDULER = ThreadPoolScheduler(2)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_depiction_json(line):
    jsonline = json.loads(line)

    if ID_IDENTIFIER in jsonline:
        entitfacts_sheet_id = jsonline[ID_IDENTIFIER]
    else:
        eprint("no GND identifier in EntityFacts sheet '{0}' (thread = '{1}')".format(line, current_thread().name))
        return None

    last_index_of_slash_in_ef_sid = entitfacts_sheet_id.rfind(SLASH)
    if last_index_of_slash_in_ef_sid > 0:
        gnd_identifier = entitfacts_sheet_id[last_index_of_slash_in_ef_sid + 1:]
    else:
        eprint("no GND identifier in EntityFacts sheet id '{0}' (thread = '{1}')".format(entitfacts_sheet_id,
                                                                                         current_thread().name))
        return None

    if DEPICTION_IDENTIFIER in jsonline:
        depiction_json = jsonline[DEPICTION_IDENTIFIER]
    else:
        eprint(
            "no depiction information for GND identifier '{0}' in its EntityFacts sheet (thread = '{1}')".format(
                gnd_identifier, current_thread().name))
        return None

    eprint("found depiction information of GND identifier '{0}' in its EntityFacts sheet (thread = '{1}')".format(
        gnd_identifier, current_thread().name))
    depiction_json_tuple = (depiction_json, gnd_identifier)

    # time.sleep(1)

    return depiction_json_tuple


def get_picture_url(depiction_json, gnd_identifier):
    if ID_IDENTIFIER in depiction_json:
        picture_url = depiction_json[ID_IDENTIFIER]
    else:
        eprint(
            "no picture URL for GND identifier '{0}' in depiction information '{1}' of its EntityFacts sheet (thread = '{2}')".format(
                gnd_identifier, depiction_json, current_thread().name))
        return None

    last_index_of_dot_in_picture_url = picture_url.rfind(DOT)
    if last_index_of_dot_in_picture_url > 0:
        file_ending = picture_url[last_index_of_dot_in_picture_url + 1:]
    else:
        eprint("no file ending found in picture URL '{0}' of GND identifier '{1}' (thread = '{2}')".format(picture_url,
                                                                                                           gnd_identifier,
                                                                                                           current_thread().name))
        return None

    file_name = IMAGE_PREFIX + gnd_identifier + DOT + file_ending

    eprint(
        "found image URL of GND identifier '{0}' in its depiction information (thread = '{1}')".format(gnd_identifier,
                                                                                                       current_thread().name))

    result_tuple = (picture_url, file_name, gnd_identifier)
    return result_tuple


def get_thumbnail_url(depiction_json, gnd_identifier):
    if THUMBNAIL_IDENTIFIER in depiction_json:
        thumbnail_json = depiction_json[THUMBNAIL_IDENTIFIER]
    else:
        eprint(
            "no thumbnail URL for GND identifier '{0}' in depiction information '{1}' of its EntityFacts sheet (thread = '{2}')".format(
                gnd_identifier, depiction_json, current_thread().name))
        return None

    if ID_IDENTIFIER in thumbnail_json:
        thumbnail_url = thumbnail_json[ID_IDENTIFIER]
    else:
        eprint(
            "no thumbnail URL for GND identifier '{0}' in depiction information '{1}' of its EntityFacts sheet (thread = '{2}')".format(
                gnd_identifier, thumbnail_json, current_thread().name))
        return None

    last_index_of_dot_in_thumbnail_url = thumbnail_url.rfind(DOT)
    if last_index_of_dot_in_thumbnail_url > 0:
        last_part_of_thumbnail_url = thumbnail_url[last_index_of_dot_in_thumbnail_url + 1:]
    else:
        eprint("no last part found in thumbail URL '{0}' of GND identifier '{1}' (thread = '{2}')".format(thumbnail_url,
                                                                                                          gnd_identifier,
                                                                                                          current_thread().name))
        return None

    last_index_of_question_mark_in_thumbnail_url = last_part_of_thumbnail_url.rfind(QUESTION_MARK)
    if last_index_of_question_mark_in_thumbnail_url > 0:
        file_ending = last_part_of_thumbnail_url[:last_index_of_question_mark_in_thumbnail_url]
    else:
        eprint(
            "no file ending found in thumbail URL '{0}' of GND identifier '{1}' (thread = '{2}')".format(thumbnail_url,
                                                                                                         gnd_identifier,
                                                                                                         current_thread().name))
        return None

    file_name = THUMBNAIL_PREFIX + gnd_identifier + DOT + file_ending

    eprint(
        "found thumbnail URL of GND identifier '{0}' in its depiction information (thread = '{1}')".format(
            gnd_identifier,
            current_thread().name))

    result_tuple = (thumbnail_url, file_name, gnd_identifier)

    # time.sleep(0.5)

    return result_tuple


def do_request(image_uri, gnd_identifier, content_type, http_headers):
    eprint(
        "try to retrieve {0} for GND identifier '{1}' from URL '{2}' (thread = '{3}')".format(content_type,
                                                                                              gnd_identifier,
                                                                                              image_uri,
                                                                                              current_thread().name))
    # time.sleep(2)
    response = requests.get(image_uri, headers=http_headers, timeout=60)
    if response.status_code != 200:
        content = response.content.decode('utf-8')
        eprint("couldn't fetch {0} for GND identifier '{1}' from URL '{2}' got a '{3}' ('{4}') (thread = '{5}')".format(
            content_type, gnd_identifier, image_uri, response.status_code, content, current_thread().name))
        return None

    response_body = response.content
    response.close()
    eprint("retrieved {0} for GND identifier '{1}' (thread = '{2}')".format(content_type, gnd_identifier,
                                                                            current_thread().name))
    return response_body


def retrieve_content_obs(request_url_tuple, files_directory, content_type, http_headers):
    file_name = request_url_tuple[1]
    absolute_file_path = os.path.join(files_directory, file_name)
    input_tuple = (request_url_tuple[0], absolute_file_path, request_url_tuple[2])
    return rx.of(input_tuple).pipe(op.map(lambda r_url_tuple: retrieve_content(r_url_tuple[0], r_url_tuple[1],
                                                                               r_url_tuple[2], content_type,
                                                                               http_headers)),
                                   op.filter(lambda value1: value1 is not None))


def retrieve_content(request_url, absolute_file_path, gnd_identifier, content_type, http_headers):
    response = do_request(request_url, gnd_identifier, content_type, http_headers)
    if response is None:
        return None
    response_tuple = (response, absolute_file_path, gnd_identifier)
    return response_tuple


def write_content_to_file_obs(response_tuple_obs, content_type):
    return response_tuple_obs.pipe(op.map(lambda response_tuple: write_content_to_file(response_tuple[0],
                                                                                       response_tuple[1],
                                                                                       response_tuple[2],
                                                                                       content_type)))


def write_content_to_file(response_bytes, absolute_file_path, gnd_identifier, content_type):
    eprint(
        "try to write {0} for GND identifier '{1}' (thread = '{2}')".format(content_type, gnd_identifier,
                                                                            current_thread().name))
    file = open(absolute_file_path, 'wb')
    file.write(response_bytes)
    file.close()
    eprint("write {0} for GND identifier '{1}' (thread = '{2}')".format(content_type, gnd_identifier,
                                                                        current_thread().name))
    return gnd_identifier


def push_input(observer, scheduler):
    for line in sys.stdin:
        observer.on_next(line)
    return observer.on_completed()


def do_harvesting(source_obs,
                  get_url_function,
                  http_headers,
                  content_type,
                  files_directory,
                  harvesting_scheduler):
    all_in_one_harvesting = source_obs.pipe(
        op.map(lambda depiction_json_tuple: get_url_function(depiction_json_tuple[0],
                                                             depiction_json_tuple[1])),
        op.filter(lambda value: value is not None),
        op.map(lambda url_tuple: retrieve_content_obs(url_tuple, files_directory, content_type, http_headers)),
        op.map(lambda response_tuple_obs: write_content_to_file_obs(response_tuple_obs, content_type)),
        op.flat_map(lambda x: x))

    all_in_one_harvesting.subscribe(
        on_next=lambda gnd_identifier: eprint(
            "PROCESSED {0} of GND identifier '{1}': {2}".format(content_type, gnd_identifier,
                                                                current_thread().name)),
        on_error=lambda e: eprint(e),
        on_completed=lambda: eprint("PROCESS {0}s harvesting done!".format(content_type)),
        scheduler=harvesting_scheduler)


def run():
    parser = argparse.ArgumentParser(prog='entityfactspicturesharvester',
                                     description='Reads depiction information (images URLs) from given EntityFacts sheets (as line-delimited JSON records) and retrieves and stores the pictures and thumbnails contained in this information.',
                                     epilog='example: entityfactspicturesharvester < [INPUT LINE-DELIMITED JSON FILE WITH ENTITYFACTS SHEETS]',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    optional_arguments = parser._action_groups.pop()

    required_arguments = parser.add_argument_group('required arguments')
    required_arguments.add_argument('-entityfacts-pictures-dir', type=str,
                                    help='The directory, where the images and thumbnails from the depiction information in the EntityFacts sheets should be stored',
                                    dest='entityfacts_pictures_directory', required=True)

    parser._action_groups.append(optional_arguments)

    args = parser.parse_args()

    if hasattr(args, 'help') and args.help:
        parser.print_usage(sys.stderr)
        exit(-1)

    entityfacts_pictures_directory = args.entityfacts_pictures_directory

    hostname = socket.getfqdn()
    user_agent = USER_AGENT_PATTERN.format(hostname)
    http_headers = {USER_AGENT_HTTP_HEADER_KEY: user_agent}

    source = rx.create(push_input)

    depiction_json_connectable_obs = source.pipe(op.map(lambda line: get_depiction_json(line)),
                                                 op.filter(lambda value: value is not None),
                                                 op.publish())

    # picture harvesting
    do_harvesting(depiction_json_connectable_obs,
                  get_picture_url,
                  http_headers,
                  PICTURE_CONTENT_TYPE,
                  entityfacts_pictures_directory,
                  PICTURE_THREAD_POOL_SCHEDULER)

    # thumbnail harvesting
    do_harvesting(depiction_json_connectable_obs,
                  get_thumbnail_url,
                  http_headers,
                  THUMBNAIL_CONTENT_TYPE,
                  entityfacts_pictures_directory,
                  THUMBNAIL_THREAD_POOL_SCHEDULER)

    depiction_json_connectable_obs.connect()


if __name__ == "__main__":
    run()
