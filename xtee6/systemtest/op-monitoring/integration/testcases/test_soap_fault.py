#!/usr/bin/env python3

# Test case for verifying that the operational monitoring related data of a
# SOAP fault response are stored by the operational monitoring daemon.

import os
import sys
import time
import xml.dom.minidom as minidom

sys.path.append('..')
import python_common as common

def _expected_keys_and_values_of_unknown_service_query_rec(
        xroad_message_id, security_server_address, security_server_type):
    return [
        ("clientMemberClass", "GOV"),
        ("clientMemberCode", "00000001"),
        ("clientSecurityServerAddress", "xtee9.ci.kit"),
        ("clientSubsystemCode", "System1"),
        ("clientXRoadInstance", "XTEE-CI-XM"),
        ("messageId", xroad_message_id),
        ("messageProtocolVersion", "4.0"),
        ("requestAttachmentCount", 0),
        ("requestSoapSize", 1202),
        ("securityServerInternalIp", security_server_address),
        ("securityServerType", security_server_type),
        ("serviceCode", "xroadGetDate"),
        ("serviceMemberClass", "GOV"),
        ("serviceMemberCode", "00000000"),
        ("serviceSecurityServerAddress", "xtee8.ci.kit"),
        ("serviceSubsystemCode", "Center"),
        ("serviceVersion", "v1"),
        ("serviceXRoadInstance", "XTEE-CI-XM"),
        ("soapFaultCode", "Server.ServerProxy.UnknownService"),
        ("soapFaultString", "Unknown service: SERVICE:XTEE-CI-XM/GOV/00000000/Center/xroadGetDate/v1"),
        ("succeeded", False),
    ]

def _expected_keys_and_values_of_unknown_member_query_rec(
        xroad_message_id, security_server_address, security_server_type):
    return [
        ("clientMemberClass", "GOV"),
        ("clientMemberCode", "00000001"),
        ("clientSecurityServerAddress", "xtee9.ci.kit"),
        ("clientSubsystemCode", "System666"),
        ("clientXRoadInstance", "XTEE-CI-XM"),
        ("messageId", xroad_message_id),
        ("messageProtocolVersion", "4.0"),
        ("requestSoapSize", 1250),
        ("securityServerInternalIp", security_server_address),
        ("securityServerType", security_server_type),
        ("serviceCode", "xroadGetRandom"),
        ("serviceMemberClass", "GOV"),
        ("serviceMemberCode", "00000000"),
        ("serviceSubsystemCode", "Center"),
        ("serviceVersion", "v1"),
        ("serviceXRoadInstance", "XTEE-CI-XM"),
        ("soapFaultCode", "Server.ClientProxy.UnknownMember"),
        ("soapFaultString", "Client 'SUBSYSTEM:XTEE-CI-XM/GOV/00000001/System666' not found"),
        ("succeeded", False),
    ]

def _expected_keys_and_values_of_soap_fault_query_rec(
        xroad_message_id, security_server_address, security_server_type):
    return [
        ("clientMemberClass", "GOV"),
        ("clientMemberCode", "00000001"),
        ("clientSecurityServerAddress", "xtee9.ci.kit"),
        ("clientSubsystemCode", "System1"),
        ("clientXRoadInstance", "XTEE-CI-XM"),
        ("messageId", xroad_message_id),
        ("messageIssue", "faultPlease"),
        ("messageProtocolVersion", "4.0"),
        ("requestAttachmentCount", 0),
        ("requestSoapSize", 1291),
        ("securityServerInternalIp", security_server_address),
        ("securityServerType", security_server_type),
        ("serviceCode", "xroadGetRandom"),
        ("serviceMemberClass", "GOV"),
        ("serviceMemberCode", "00000000"),
        ("serviceSecurityServerAddress", "xtee8.ci.kit"),
        ("serviceSubsystemCode", "Center"),
        ("serviceVersion", "v1"),
        ("serviceXRoadInstance", "XTEE-CI-XM"),
        ("soapFaultCode", "foo.bar.testFault"),
        ("soapFaultString", "Anything can happen in life, especially faults"),
        ("succeeded", False),
    ]

def run(client_security_server_address, producer_security_server_address,
        request_template_dir):
    unknown_member_query_template_filename = os.path.join(
            request_template_dir, "unknown_member_query_template.xml")
    unknown_service_query_template_filename = os.path.join(
            request_template_dir, "unknown_service_query_template.xml")
    soap_fault_query_template_filename = os.path.join(
            request_template_dir, "soap_fault_query_template.xml")
    query_data_client_template_filename = os.path.join(
            request_template_dir, "query_operational_data_client_ss_owner_template.xml")
    query_data_producer_template_filename = os.path.join(
            request_template_dir, "query_operational_data_producer_ss_owner_template.xml")

    timestamp_before_request = common.generate_timestamp()

    message_id_serverproxy = common.generate_message_id()
    print("\nGenerated message ID %s for X-Road request to unknown service" % (
        message_id_serverproxy, ))

    ### Regular and operational data requests and the relevant checks

    print("\n---- Sending an X-Road request to an unknown service to the client's " \
            "security server ----\n")

    request_contents = common.format_xroad_request_template(
            unknown_service_query_template_filename, message_id_serverproxy)
    print("Generated the following X-Road request: \n")
    print(request_contents)

    response = common.post_xml_request(
            client_security_server_address, request_contents)

    print("\nReceived the following X-Road response: \n")
    xml = minidom.parseString(common.clean_whitespace(response.text))
    print(xml.toprettyxml())

    common.assert_soap_fault(xml)

    message_id_clientproxy = common.generate_message_id()
    print("\nGenerated message ID %s for X-Road request from unknown member" % (
        message_id_clientproxy, ))

    print("\n---- Sending an X-Road request from an unknown member to the " \
            "client's security server ----\n")

    request_contents = common.format_xroad_request_template(
            unknown_member_query_template_filename, message_id_clientproxy)
    print("Generated the following X-Road request: \n")
    print(request_contents)

    response = common.post_xml_request(
            client_security_server_address, request_contents)

    print("\nReceived the following X-Road response: \n")
    xml = minidom.parseString(common.clean_whitespace(response.text))
    print(xml.toprettyxml())

    common.assert_soap_fault(xml)

    message_id_service = common.generate_message_id()
    print("\nGenerated message ID %s for X-Road request that will cause a SOAP fault" % (
        message_id_service, ))
    
    print("\n---- Sending an X-Road request that will cause a SOAP fault to the " \
            "client's security server ----\n")

    request_contents = common.format_xroad_request_template(
            soap_fault_query_template_filename, message_id_service)
    print("Generated the following X-Road request: \n")
    print(request_contents)
 
    response = common.post_xml_request(
            client_security_server_address, request_contents)

    print("\nReceived the following X-Road response: \n")
    xml = minidom.parseString(common.clean_whitespace(response.text))
    print(xml.toprettyxml())

    common.assert_soap_fault(xml)

    # Wait a couple of seconds for the operational data to be stored with some certainty.
    time.sleep(3)
    timestamp_after_request = common.generate_timestamp()
    
    # Now make operational data requests to both security servers and check the
    # response payloads.

    print("\n---- Sending an operational data request to the client's security server ----\n")

    message_id = common.generate_message_id()
    message_id_client = message_id
    print("Generated message ID %s for query data request" % (message_id, ))

    request_contents = common.format_query_operational_data_request_template(
            query_data_client_template_filename, message_id,
            timestamp_before_request - 5, timestamp_after_request + 5)

    print("Generated the following query data request for the client's security server: \n")
    print(request_contents)

    response = common.post_xml_request(
            client_security_server_address, request_contents,
            get_raw_stream=True)
    mime_parts, raw_response = common.parse_multipart_response(response)
 
    if mime_parts:
        soap_part, record_count = common.get_multipart_soap_and_record_count(mime_parts[0])
        common.print_multipart_soap_and_record_count(soap_part, record_count)

        json_payload = common.get_multipart_json_payload(mime_parts[1])

        # Check the presence of all the required fields in at least one JSON structure.

        # The record describing the X-Road request that caused a fault in server proxy
        common.assert_present_in_json(
                json_payload, _expected_keys_and_values_of_unknown_service_query_rec(
                    message_id_serverproxy, client_security_server_address, "Client"))
 
        # The record describing the X-Road request that caused a fault in client proxy
        common.assert_present_in_json(
                json_payload, _expected_keys_and_values_of_unknown_member_query_rec(
                    message_id_clientproxy, client_security_server_address, "Client"))

        # The record describing the X-Road request that caused a fault in test service
        common.assert_present_in_json(
                json_payload, _expected_keys_and_values_of_soap_fault_query_rec(
                    message_id_service, client_security_server_address, "Client"))

        # Check if the timestamps in the response are in the expected range.
        common.assert_expected_timestamp_values(
                json_payload, timestamp_before_request, timestamp_after_request)

        common.print_multipart_query_data_response(json_payload)

    else:
        common.parse_and_check_soap_response(raw_response)

    print("\n---- Sending an operational data request to the producer's " \
                "security server ----\n")

    message_id = common.generate_message_id()
    message_id_producer = message_id
    print("\nGenerated message ID %s for query data request" % (message_id, ))

    request_contents = common.format_query_operational_data_request_template(
            query_data_producer_template_filename, message_id,
            timestamp_before_request - 5, timestamp_after_request + 5)
    print("Generated the following query data request for the producer's " \
            "security server: \n")
    print(request_contents)

    response = common.post_xml_request(
            producer_security_server_address, request_contents,
            get_raw_stream=True)
    mime_parts, raw_response = common.parse_multipart_response(response)

    if mime_parts:
        soap_part, record_count = common.get_multipart_soap_and_record_count(mime_parts[0])
        common.print_multipart_soap_and_record_count(soap_part, record_count, is_client=False)
 
        json_payload = common.get_multipart_json_payload(mime_parts[1])

        # Check the presence of all the required fields in at least one JSON structure.

        # The record describing the X-Road request that caused a fault in server proxy
        common.assert_present_in_json(
                json_payload, _expected_keys_and_values_of_unknown_service_query_rec(
                    message_id_serverproxy, producer_security_server_address, "Producer"))

        # The record describing the X-Road request that caused a fault in test service
        common.assert_present_in_json(
                json_payload, _expected_keys_and_values_of_soap_fault_query_rec(
                    message_id_service, producer_security_server_address, "Producer"))

        # Check timestamp values
        common.assert_expected_timestamp_values(
                json_payload, timestamp_before_request, timestamp_after_request)
 
        common.print_multipart_query_data_response(json_payload)
 
    else:
        common.parse_and_check_soap_response(raw_response)
