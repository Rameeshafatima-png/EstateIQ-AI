# EstateIQ AI Dataset

## Dataset used

**Zameen.com 2022 raw property data**: 29,078 house listings from Zameen.com, Pakistan's largest property portal, scraped in September 2022.

Source repository: https://github.com/huzefakhan/Zameen.com-2022-latest-Raw-Data-Set-Realstate
Original website: https://www.zameen.com

Cities: Lahore, Karachi, Islamabad, Peshawar. All listings are houses; about 95% are for sale.

**Licence note:** the source repository does not state a licence, and the data was scraped from a public website. It is used here for learning and a course project, not commercial use. If you need a clearly licensed dataset, Property Data for Pakistan by CHISEL @ LUMS (Creative Commons Attribution, 2020) is the alternative: https://www.opendata.com.pk/dataset/property-data-for-pakistan

## Files

| File | What it is |
|---|---|
| `properties_raw.csv` | The `property_details` table from the source, trimmed to 13 columns |
| `properties_clean.csv` | Output of `python -m analysis.real_estate_analysis` |
| `properties_sample.csv` | Three example rows from Step 1 |

## Cleaning rules

- Keep "For Sale" listings only (rent prices are on a different scale)
- Convert area to square feet: 1 marla = 272.25 sq ft, 1 kanal = 20 marla, 1 sq yd = 9 sq ft
- Keep bedrooms and bathrooms between 1 and 10 (0 means missing or a plot)
- Keep areas from 450 to 25,000 sq ft
- Drop the lowest and highest 1% of price per square foot
- Result: 24,918 of 29,078 rows
