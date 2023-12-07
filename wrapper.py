import pandas as pd
import numpy as np
from steam_parser import df_api, df_tags

def XML5(df, tags):
        xml_list = []
        part0 = """<?xml version='1.0'?>\n<bib>"""
        xml_list.append(part0)
        part2, part3 ="",""
        unique_app_ids = df['appid'].drop_duplicates().dropna().to_list()
        for i, game_id in enumerate(unique_app_ids):
                part1 = f"""
        <game id= "g{df["appid"][i]}">
                <title>{df['name'][i]}</title>
                <price>{int(df['price'][i])/100}</price>
                <publisher>{df['publisher'][i]}</publisher>
                <developer>{df['developer'][i]}</developer>
                """
                tags = df_tags[df_tags["appid"] == game_id]
                part2 = ''.join([f'\t\t\t\t<tag name="{t}">' for t in tags["tag"].to_list()[:3]])
                review_df = df[df['appid'] == game_id].reset_index()
                for f, useless in enumerate(review_df['name'][0:4].to_list()):
                        part30 = f"""
                        <review id= "r{review_df["recommendationid"][f]}">
                                <review_text>{review_df['review'][f]}</review_text>
                                <comment_time>{review_df['timestamp_created'][f]}</comment_time>
                                <upvotes>{review_df['votes_up'][f]}</upvotes>
                                <customerid>c{review_df['steamid'][f]}</customerid>
                        </review>
                        """
                        part3 = part3 + part30  
                part4 = """
        </game>"""
                xml_game = "".join([part1, part2, part3, part4])
                xml_list.append(xml_game)

        part5 = """\n</bib>"""
        xml_list.append(part5)
        with open("WRITE_XML.xml", "w+") as x:
                x.write("".join(xml_list))
                x.close()

XML5(df_api, df_tags)