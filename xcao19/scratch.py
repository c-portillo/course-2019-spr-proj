import reverse_geocoder as rg 

coord = (42.3425944446, -71.0794207018)

res = rg.search(coord)
print(res)