#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
------------------------------------------------------------------------------------------------------------------------
tests.py
Copyright (C) 2019-20 - NFStream Developers
This file is part of NFStream, a Flexible Network Data Analysis Framework (https://www.nfstream.org/).
NFStream is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.
NFStream is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with NFStream.
If not, see <http://www.gnu.org/licenses/>.
------------------------------------------------------------------------------------------------------------------------
"""

import unittest
import pandas as pd
import json
import os
import csv
from nfstream import NFStreamer, NFPlugin
from nfstream.plugins import SPLT


def get_files_list(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.pcap' == file[-5:]:
                files.append(os.path.join(r, file))
    files.sort()
    return files


def get_app_dict(path):
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        app = {}
        for row in reader:
            try:
                app[row['ndpi_proto']]['bytes'] += int(row['s_to_c_bytes']) + int(row['c_to_s_bytes'])
                app[row['ndpi_proto']]['flows'] += 1
                app[row['ndpi_proto']]['pkts'] += int(row['s_to_c_pkts']) + int(row['c_to_s_pkts'])
            except KeyError:
                app[row['ndpi_proto']] = {"bytes": 0, "flows": 0, "pkts": 0}
                app[row['ndpi_proto']]["bytes"] += int(row['s_to_c_bytes']) + int(row['c_to_s_bytes'])
                app[row['ndpi_proto']]["flows"] += 1
                app[row['ndpi_proto']]['pkts'] += int(row['s_to_c_pkts']) + int(row['c_to_s_pkts'])
    return app


def build_ndpi_dict(path):
    list_gt = get_files_list(path)
    ndpi = {}
    for file in list_gt:
        ndpi[file.split('/')[-1]] = get_app_dict(file)
    return ndpi


class OnePacketExpire(NFPlugin):
    def on_init(self, packet, flow):
        flow.expiration_id = -1


class FourPacketExpire(NFPlugin):
    def on_update(self, packet, flow):
        if flow.bidirectional_packets == 4:
            flow.expiration_id = -1


class TestMethods(unittest.TestCase):

    def test_parameters_handling(self):
        print("\n----------------------------------------------------------------------")
        value_errors = 0
        source = ["inexisting.pcap", "lo", "lo0", 22]
        for x in source:
            try:
                for flow in NFStreamer(source=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        decode_tunnels = [33, "True"]
        for x in decode_tunnels:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', decode_tunnels=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        bpf_filter = ["my filter", 11]
        for x in bpf_filter:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', bpf_filter=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        promiscuous_mode = ["yes", 89]
        for x in promiscuous_mode:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', promiscuous_mode=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        snapshot_length = ["largest", -1]
        for x in snapshot_length:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', snapshot_length=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        idle_timeout = [-1, "idle"]
        for x in idle_timeout:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', idle_timeout=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        active_timeout = [-1, "active"]
        for x in active_timeout:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', active_timeout=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        accounting_mode = [-1, 5, 'ip']
        for x in accounting_mode:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', accounting_mode=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        udps = [lambda y: y+1, "NFPlugin"]
        for x in udps:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', udps=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        n_dissections = ["yes", -1, 256]
        for x in n_dissections:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', n_dissections=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        statistical_analysis = ["yes", 89]
        for x in statistical_analysis:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', statistical_analysis=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        splt_analysis = [-1, 256, "yes"]
        for x in splt_analysis:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', splt_analysis=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        n_meters = ["yes", -1]
        for x in n_meters:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', n_meters=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        performance_report = ["yes", -1]
        for x in performance_report:
            try:
                for flow in NFStreamer(source='tests/pcap/google_ssl.pcap', performance_report=x):
                    print(flow)
            except ValueError:
                value_errors += 1
        self.assertEqual(value_errors, 31)
        print("{}\t: \033[94mOK\033[0m".format(".Test parameters handling".ljust(60, ' ')))

    def test_expiration_management(self):
        print("\n----------------------------------------------------------------------")
        # Idle expiration
        streamer_expiration = NFStreamer(source='tests/pcap/google_ssl.pcap', idle_timeout=0,
                                         n_meters=int(os.getenv('MAX_NFMETERS', 0)))
        last_id = 0
        for flow in streamer_expiration:
            last_id = flow.id
        self.assertEqual(last_id, 27)
        # Active expiration
        streamer_expiration = NFStreamer(source='tests/pcap/google_ssl.pcap', active_timeout=0,
                                         n_meters=int(os.getenv('MAX_NFMETERS', 0)))
        last_id = 0
        for flow in streamer_expiration:
            last_id = flow.id
        self.assertEqual(last_id, 27)
        # Custom expiration

        streamer_expiration = NFStreamer(source='tests/pcap/google_ssl.pcap', udps=OnePacketExpire(),
                                         n_meters=int(os.getenv('MAX_NFMETERS', 0)))
        last_id = 0
        for flow in streamer_expiration:
            last_id = flow.id
        self.assertEqual(last_id, 27)

        streamer_expiration = NFStreamer(source='tests/pcap/google_ssl.pcap', udps=FourPacketExpire(),
                                         n_meters=int(os.getenv('MAX_NFMETERS', 0)))
        last_id = 0
        for flow in streamer_expiration:
            last_id = flow.id
        self.assertEqual(last_id, 6)

        print("{}\t: \033[94mOK\033[0m".format(".Test expiration management".ljust(60, ' ')))

    def test_statistical(self):
        print("\n----------------------------------------------------------------------")
        statistical_streamer = NFStreamer(source='tests/pcap/google_ssl.pcap', statistical_analysis=True,
                                          accounting_mode=1, n_meters=int(os.getenv('MAX_NFMETERS', 0)))
        for flow in statistical_streamer:
            self.assertEqual(flow.id, 0)
            self.assertEqual(flow.expiration_id, 0)
            self.assertEqual(flow.src_ip, '172.31.3.224')
            self.assertEqual(flow.src_ip_is_private, 1)
            self.assertEqual(flow.src_port, 42835)
            self.assertEqual(flow.dst_ip, '216.58.212.100')
            self.assertEqual(flow.dst_ip_is_private, 0)
            self.assertEqual(flow.dst_port, 443)
            self.assertEqual(flow.protocol, 6)
            self.assertEqual(flow.ip_version, 4)
            self.assertEqual(flow.vlan_id, 0)
            self.assertEqual(flow.bidirectional_first_seen_ms, 1434443394683)
            self.assertEqual(flow.bidirectional_last_seen_ms, 1434443401353)
            self.assertEqual(flow.bidirectional_duration_ms, 6670)
            self.assertEqual(flow.bidirectional_packets, 28)
            self.assertEqual(flow.bidirectional_bytes, 8696)
            self.assertEqual(flow.src2dst_first_seen_ms, 1434443394683)
            self.assertEqual(flow.src2dst_last_seen_ms, 1434443401353)
            self.assertEqual(flow.src2dst_duration_ms, 6670)
            self.assertEqual(flow.src2dst_packets, 16)
            self.assertEqual(flow.src2dst_bytes, 1288)
            self.assertEqual(flow.dst2src_first_seen_ms, 1434443394717)
            self.assertEqual(flow.dst2src_last_seen_ms, 1434443401308)
            self.assertEqual(flow.dst2src_duration_ms, 6591)
            self.assertEqual(flow.dst2src_packets, 12)
            self.assertEqual(flow.dst2src_bytes, 7408)
            self.assertEqual(flow.bidirectional_min_ps, 40)
            self.assertAlmostEqual(flow.bidirectional_mean_ps, 310.57142857142856)
            self.assertAlmostEqual(flow.bidirectional_stddev_ps, 500.54617788019937)
            self.assertEqual(flow.bidirectional_max_ps, 1470)
            self.assertEqual(flow.src2dst_min_ps, 40)
            self.assertAlmostEqual(flow.src2dst_mean_ps, 80.49999999999999)
            self.assertAlmostEqual(flow.src2dst_stddev_ps, 89.55519713189922)
            self.assertEqual(flow.src2dst_max_ps, 354)
            self.assertEqual(flow.dst2src_min_ps, 40)
            self.assertAlmostEqual(flow.dst2src_mean_ps, 617.3333333333334)
            self.assertAlmostEqual(flow.dst2src_stddev_ps, 651.4524099458397)
            self.assertEqual(flow.dst2src_max_ps, 1470)
            self.assertEqual(flow.bidirectional_min_piat_ms, 0)
            self.assertAlmostEqual(flow.bidirectional_mean_piat_ms, 247.037037037037)
            self.assertAlmostEqual(flow.bidirectional_stddev_piat_ms, 324.04599406227237)
            self.assertEqual(flow.bidirectional_max_piat_ms, 995)
            self.assertEqual(flow.src2dst_min_piat_ms, 76)
            self.assertAlmostEqual(flow.src2dst_mean_piat_ms, 444.6666666666667)
            self.assertAlmostEqual(flow.src2dst_stddev_piat_ms, 397.60329595261277)
            self.assertEqual(flow.src2dst_max_piat_ms, 1185)
            self.assertEqual(flow.dst2src_min_piat_ms, 66)
            self.assertAlmostEqual(flow.dst2src_mean_piat_ms, 599.1818181818182)
            self.assertAlmostEqual(flow.dst2src_stddev_piat_ms, 384.78456782511904)
            self.assertEqual(flow.dst2src_max_piat_ms, 1213)
            self.assertEqual(flow.bidirectional_syn_packets, 2)
            self.assertEqual(flow.bidirectional_cwr_packets, 0)
            self.assertEqual(flow.bidirectional_ece_packets, 0)
            self.assertEqual(flow.bidirectional_urg_packets, 0)
            self.assertEqual(flow.bidirectional_ack_packets, 27)
            self.assertEqual(flow.bidirectional_psh_packets, 8)
            self.assertEqual(flow.bidirectional_rst_packets, 0)
            self.assertEqual(flow.bidirectional_fin_packets, 2)
            self.assertEqual(flow.src2dst_syn_packets, 1)
            self.assertEqual(flow.src2dst_cwr_packets, 0)
            self.assertEqual(flow.src2dst_ece_packets, 0)
            self.assertEqual(flow.src2dst_urg_packets, 0)
            self.assertEqual(flow.src2dst_ack_packets, 15)
            self.assertEqual(flow.src2dst_psh_packets, 4)
            self.assertEqual(flow.src2dst_rst_packets, 0)
            self.assertEqual(flow.src2dst_fin_packets, 1)
            self.assertEqual(flow.dst2src_syn_packets, 1)
            self.assertEqual(flow.dst2src_cwr_packets, 0)
            self.assertEqual(flow.dst2src_ece_packets, 0)
            self.assertEqual(flow.dst2src_urg_packets, 0)
            self.assertEqual(flow.dst2src_ack_packets, 12)
            self.assertEqual(flow.dst2src_psh_packets, 4)
            self.assertEqual(flow.dst2src_rst_packets, 0)
            self.assertEqual(flow.dst2src_fin_packets, 1)
        del statistical_streamer
        print("{}\t: \033[94mOK\033[0m".format(".Test statistical extraction".ljust(60, ' ')))

    def test_fingerprint_extraction(self):
        print("\n----------------------------------------------------------------------")
        fingerprint_streamer = NFStreamer(source='tests/pcap/facebook.pcap', statistical_analysis=True,
                                          accounting_mode=1, n_meters=int(os.getenv('MAX_NFMETERS', 0)))
        for flow in fingerprint_streamer:
            self.assertEqual(flow.application_name, 'TLS.Facebook')
            self.assertEqual(flow.application_category_name, 'SocialNetwork')
            self.assertEqual(flow.application_is_guessed, 0)
            self.assertTrue(flow.requested_server_name in ['facebook.com', 'www.facebook.com'])
            self.assertTrue(flow.client_fingerprint in ['bfcc1a3891601edb4f137ab7ab25b840',
                                                        '5c60e71f1b8cd40e4d40ed5b6d666e3f'])
            self.assertTrue(flow.server_fingerprint in ['2d1eb5817ece335c24904f516ad5da12',
                                                        '96681175a9547081bf3d417f1a572091'])
        del fingerprint_streamer
        print("{}\t: \033[94mOK\033[0m".format(".Test fingerprint extraction".ljust(60, ' ')))

    def test_export(self):
        print("\n----------------------------------------------------------------------")
        df = NFStreamer(source='tests/pcap/steam.pcap',
                        statistical_analysis=True, n_meters=int(os.getenv('MAX_NFMETERS', 0)),
                        n_dissections=20).to_pandas(ip_anonymization=False)
        df_anon = NFStreamer(source='tests/pcap/steam.pcap',
                             statistical_analysis=True, n_meters=int(os.getenv('MAX_NFMETERS', 0)),
                             n_dissections=20).to_pandas(ip_anonymization=True)
        self.assertEqual(df_anon.shape[0], df.shape[0])
        self.assertEqual(df_anon.shape[1], df.shape[1])
        self.assertEqual(df_anon['src_ip'].nunique(), df['src_ip'].nunique())
        self.assertEqual(df_anon['dst_ip'].nunique(), df['dst_ip'].nunique())

        total_flows = NFStreamer(source='tests/pcap/steam.pcap',
                                 statistical_analysis=True, n_meters=int(os.getenv('MAX_NFMETERS', 0)),
                                 n_dissections=20).to_csv(ip_anonymization=False)
        df_from_csv = pd.read_csv('tests/pcap/steam.pcap.csv')
        total_flows_anon = NFStreamer(source='tests/pcap/steam.pcap',
                                      statistical_analysis=True, n_meters=int(os.getenv('MAX_NFMETERS', 0)),
                                      n_dissections=20).to_csv(ip_anonymization=False)
        df_anon_from_csv = pd.read_csv('tests/pcap/steam.pcap.csv')
        self.assertEqual(total_flows, total_flows_anon)
        self.assertEqual(total_flows, df_from_csv.shape[0])
        self.assertEqual(total_flows_anon, df_anon_from_csv.shape[0])
        self.assertEqual(total_flows, df.shape[0])
        self.assertEqual(total_flows_anon, df_anon.shape[0])
        print("{}\t: \033[94mOK\033[0m".format(".Test export interfaces".ljust(60, ' ')))

    def test_bpf(self):
        print("\n----------------------------------------------------------------------")
        streamer_test = NFStreamer(source='tests/pcap/facebook.pcap',
                                   bpf_filter="src port 52066 or dst port 52066",
                                   n_meters=int(os.getenv('MAX_NFMETERS', 0)))
        last_id = 0
        for flow in streamer_test:
            last_id = flow.id
            self.assertEqual(flow.src_port, 52066)
        self.assertEqual(last_id, 0)
        del streamer_test
        print("{}\t: \033[94mOK\033[0m".format(".Test BPF".ljust(60, ' ')))

    def test_ndpi_integration(self):
        files = get_files_list("tests/pcap/")
        ground_truth_ndpi = build_ndpi_dict("tests/result/")
        print("\n----------------------------------------------------------------------")
        print(".Test nDPI integration on {} applications:".format(len(files)))
        ok_files = []
        for test_file in files:
            streamer_test = NFStreamer(source=test_file, n_dissections=20, n_meters=int(os.getenv('MAX_NFMETERS', 0)),
                                       idle_timeout=31556952, active_timeout=31556952)
            test_case_name = test_file.split('/')[-1]
            result = {}
            for flow in streamer_test:
                if flow.application_name != 'Unknown':
                    try:
                        result[flow.application_name]['bytes'] += flow.bidirectional_bytes
                        result[flow.application_name]['flows'] += 1
                        result[flow.application_name]['pkts'] += flow.bidirectional_packets
                    except KeyError:
                        result[flow.application_name] = {"bytes": flow.bidirectional_bytes,
                                                         'flows': 1, 'pkts': flow.bidirectional_packets}
            if result == ground_truth_ndpi[test_case_name]:
                ok_files.append(test_case_name)
                print("{}\t: \033[94mOK\033[0m".format(test_case_name.ljust(60, ' ')))
            else:
                print("{}\t: \033[31mKO\033[0m".format(test_case_name.ljust(60, ' ')))
        self.assertEqual(len(files), len(ok_files))

    def test_splt(self):
        print("\n----------------------------------------------------------------------")
        splt_df = NFStreamer(source='tests/pcap/google_ssl.pcap', splt_analysis=5,
                             n_meters=int(os.getenv('MAX_NFMETERS', 0)),
                             udps=SPLT(sequence_length=5, accounting_mode=0)).to_pandas()
        direction = json.loads(splt_df["udps.splt_direction"][0])
        ps = json.loads(splt_df["udps.splt_ps"][0])
        piat = json.loads(splt_df["udps.splt_piat_ms"][0])
        ndirection = json.loads(splt_df["splt_direction"][0])
        nps = json.loads(splt_df["splt_ps"][0])
        npiat = json.loads(splt_df["splt_piat_ms"][0])
        self.assertEqual(direction, [0, 1, 0, 0, 1])
        self.assertEqual(ps, [58, 60, 54, 180, 60])
        self.assertEqual(piat, [0, 34, 134, 144, 35])
        self.assertEqual(direction, ndirection)
        self.assertEqual(ps, nps)
        self.assertEqual(piat, npiat)
        print("{}\t: \033[94mOK\033[0m".format(".Test SPLT analysis".ljust(60, ' ')))


if __name__ == '__main__':
    unittest.main()
