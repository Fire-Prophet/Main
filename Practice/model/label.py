forest_type_map = {
    "0":"비산림/무립목지","1":"침엽수림","2":"활엽수림","3":"혼효림","4":"죽림"
}
species_group_map = {
    "11":"소나무","12":"잣나무", … ,"99":"기타"
}
diameter_class_map = {
    "0":"치수(<6cm)","1":"소경목(6~18cm)","2":"중경목(18~30cm)","3":"대경목(>30cm)"
}
# 나머지도 동일하게…



# 매핑 적용 예시
gdf["ForestType"] = gdf["FRTP_CD"].map(forest_type_map)
gdf["Species"]    = gdf["KOFTR_GROU_CD"].map(species_group_map)
gdf["DiaClass"]   = gdf["DMCLS_CD"].map(diameter_class_map)