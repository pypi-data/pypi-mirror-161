# Skill level points
skill_level_points = {
    '00': 25,
    '0': 25,
    'A': 25,
    'B': 10,
    'C': 5,
    'D': 5
}

# Skill level bonus points
skill_level_bonus_points = {
    '00': 15,
    # 'High Demand': 10, # removed since March 10, 2020
    'Working in the position': 10
}

# Wange range points
wage_points = [
    [100000, 10000000, 50],
    [97500, 99999, 38],
    [95000, 97499, 37],
    [92500, 94999, 36],
    [90000, 92499, 35],
    [87500, 89999, 34],
    [85000, 87499, 33],
    [82500, 84999, 32],
    [80000, 82499, 31],
    [77500, 79999, 30],
    [75000, 77499, 29],
    [72500, 74999, 28],
    [70000, 72499, 27],
    [67500, 69999, 26],
    [65000, 67499, 25],
    [62500, 64999, 24],
    [60000, 62499, 23],
    [57500, 59999, 22],
    [55000, 57499, 21],
    [52500, 54999, 20],
    [50000, 52499, 19],
    [47500, 49999, 18],
    [45000, 47499, 17],
    [42500, 44999, 16],
    [40000, 42499, 15],
    [38750, 39999, 14],
    [37500, 38749, 13],
    [36250, 37499, 12],
    [35000, 36249, 11],
    [33750, 34999, 10],
    [32500, 33749, 9],
    [31250, 32499, 8],
    [30000, 31249, 7],
    [28750, 29999, 6],
    [27500, 28749, 5],
    [26250, 27499, 4],
    [25000, 26249, 3],
    [0, 25000, 0]
]

# Region points.
region_points = {
    'Stikine': 10,
    'Central Coast': 10,
    'Northern Rockies': 10,
    'Mount Waddington': 10,
    'Skeena-Queen Charlotte': 10,
    'Powell River': 10,
    'Sunshine Coast': 10,
    'Kootenay-Boundary': 10,
    'Alberni-Clayoquot': 10,
    'Kitimat-Stikine': 8,
    'Bulkley-Nechako': 8,
    'Squamish-Lillooet': 8,
    'Strathcona': 8,
    'Columbia-Shuswap': 8,
    'East Kootenay': 8,
    'Peace River': 6,
    'Comox Valley': 6,
    'Cariboo': 6,
    'Central Kootenay': 6,
    'Okanagan-Similkameen': 4,
    'Cowichan Valley': 4,
    'North Okanagan': 4,
    'Fraser-Fort George': 4,
    'Thompson-Nicola': 2,
    'Nanaimo': 2,
    'Central Okanagan': 2,
    'Capital': 2,
    'Fraser Valley': 2,
    'Greater Vancouver': 0
}

# mapping the job bank region index to areas #TODO:需要完成其他的
region_index = {
    'Stikine': 10,
    'Central Coast': 10,
    'Northern Rockies': 80,
    'Mount Waddington': 10,
    'Skeena-Queen Charlotte': 10,
    'Powell River': 82,
    'Sunshine Coast': 10,
    'Kootenay-Boundary': 76,
    'Alberni-Clayoquot': 10,
    'Kitimat-Stikine': 8,
    'Bulkley-Nechako': 8,
    'Squamish-Lillooet': 77,
    'Strathcona': 8,
    'Columbia-Shuswap': 8,
    'East Kootenay': 76,
    'Peace River': 6,
    'Comox Valley': 6,
    'Cariboo': 75,
    'Central Kootenay': 76,
    'Okanagan-Similkameen': 81,
    'Cowichan Valley': 4,
    'North Okanagan': 81,
    'Fraser-Fort George': 4,
    'Thompson-Nicola': 2,
    'Nanaimo': 82,
    'Central Okanagan': 81,
    'Capital': 2,
    'Fraser Valley': 2,
    'Greater Vancouver': 77
}

# work experience points, which is based on months
work_experience_points = [
    [60, 60000, 15],
    [48, 59, 12],
    [36, 47, 9],
    [24, 35, 6],
    [12, 23, 3],
    [1, 11, 1],
    [0, 0, 0]
]

# Education points
education_points = {    # TODO: 修改为和EE统一的
    'Doctor':17,
    'Master': 17,
    'Bachelor': 11,
    'Post Graduate Certificate or Diploma':11,
    'Trades certification':11,
    'Associate Degree': 4,
    'Non-trades certification or Diploma': 2,
    'Secondary': 0
}
education_diplomas=['Two more post-secondary','3-year post-secondary','2-year post-secondary','1-year post-secondary']


# Education bonus points
education_bonus_points = {
    'BC Post-secondary': 8,
    'Canada Post-secondary': 6,  # Outside of BC
    'ECA': 4,  # with Education Credential Assessment
    # Successfully completed the Industry Training Authority British Columbia (ITABCs) challenge certification process
    'Trade certificate': 4,
    'Nothing': 0
}

# languange points
language_points = {
    10: 30,
    9: 26,
    8: 22,
    7: 18,
    6: 14,
    5: 10,
    4: 6,
    3: 0
}
working_in_the_position_points={
    True:10
}

one_year_experience_point={
    True:10
}

# BCPNP NOC data
# if in BC High Demand occupation list, you will get 10 more bonus points
# removed on March 10, 2022
bc_high_demand = [
    '0621', '0631', '0013', '0714', '0213', '0111', '0601', '0122', '0016', '0124', '0015', '0121', '0821', '0731',
    '0712', '0632', '0114', '0423', '0112', '0014', '0125', '0651', '0422', '0113', '0421', '0211', '0012', '0513',
    '0512', '0912', '0212', '0412', '0414', '1111', '4032', '2171', '2174', '1114', '4112', '1122', '2173', '1123',
    '4021', '2131', '4011', '4163', '1121', '5131', '4152', '4153', '2175', '5121', '4165', '2151', '1112', '4161',
    '1113', '2147', '4151', '1221', '4212', '1311', '1241', '4214', '6232', '7321', '5241', '6341', '5254', '6221',
    '1224', '4311', '6231', '6235', '2281', '2242', '6211', '1215', '1242', '1222', '2282', '1243', '2271', '4211',
    '1312', '4312', '7315', '1223', '1212', '5221', '4313', '1315', '1414', '6513', '4412', '4411', '7513', '1513',
    '1512', '1511', '3112', '3413', '3142', '3143', '3233', '3012', '3216', '3234'
]
# if in BC Tech Pilot list, the application will be more possible successful and be fast processed
# updated: June 2018
bc_tech_pilot = [
    '0131', '0213', '0512', '2131', '2132', '2133', '2134', '2147', '2171', '2172', '2173', '2174', '2175', '2221',
    '2241', '2242', '2243', '2281', '2282', '2283', '5121', '5122', '5125', '5224', '5225', '5226', '5227', '5241',
    '6221']
# New since March 10,2022
healthcare=["0311","3011","3012","3111","3112","3113","3122","3124","3125","3131","3132","3141","3142","3143","3144","3211","3212","3214","3215","3216","3217","3219","3221","3222","3223","3232","3233","3234","3237","3411","3413","4151","4152","4153","4212"]
childcare=['4214']
#BC Entry level/Semi-skilled (ELSS) eligibl NOCs in BC (in Northeast Development Region has no such limitation but live-in caregivers)
bc_elss_occupation = ['6525', '6531', '6532', '6533', '6511', '6512', '6513', '6711', '6731',
                    '6732', '6733', '6721', '6741', '6742', '9461', '9462', '9463', '9465', '9617', '9618', '7511']

special_nocs={
    "3413":"For the purposes of the BC PNP, only health care assistants / health care aides are eligible under NOC 3413."
}