import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv('vehicles_us.csv')
# Fixing data
df['model_year'] = df['model_year'].astype("Int64")
df['odometer'] = df['odometer'].astype("Int64")
# Changing 'is_4wd' column to Integer64 dtype and filled NaN with 0
df['is_4wd'] = df['is_4wd'].fillna(0).astype("Int64")
# Converting 'price' and 'days_listed' column to Int64 dtype to keep consistency
df['price'] = df['price'].astype("Int64")
df['days_listed'] = df['days_listed'].astype("Int64")

# Changing columns to category dtype
df['model'] = df['model'].astype('category')
df['condition'] = df['condition'].astype('category')
# Filling NaN values in 'cylinders' with 'unknown'
df['cylinders'] = df['cylinders'].fillna(0).astype(int)
df['cylinders'] = df['cylinders'].replace(0, 'unknown').astype('category')
df['fuel'] = df['fuel'].astype('category')
df['transmission'] = df['transmission'].astype('category')
df['type'] = df['type'].astype('category')
df['paint_color'] = df['paint_color'].astype('category')
# Filling NaN values in 'paint_color' with 'unknown'
df['paint_color'] = df['paint_color'].cat.add_categories(['unknown']).fillna('unknown')

# Converting 'date_posted' column to datetime dtype
df['date_posted'] = pd.to_datetime(df['date_posted'], errors='coerce')
# Droping rows with null 'model_year' or 'odometer' values
df = df.dropna(subset=['model_year', 'odometer'])

# Enriching data
# Extracting the make from the 'model' column and assigning them to its own 'make' column
# Keeping 'model' column as is to preserve the full model name
df['make'] = df['model'].str.split().str[0]
df['make'] = df['make'].astype('category')
# Rearranging columns in the DataFrame
df = df[['price', 'model_year', 'make', 'model', 'condition', 'cylinders', 'fuel', 'odometer', 'transmission', 'type', 'paint_color', 'is_4wd', 'date_posted', 'days_listed']]
# Droping rows with price less than $1000 and greater than $200,000 to remove obvious outliers in the data
df = df[(df['price'] >= 1000) & (df['price'] <= 200000)]




st.header("Vehicle Listings Analysis")
# Creating a new DF with 'other' vehicle type removed,
# and only including vehicles priced up to $75,000, model year 1980 and newer and miles 400,000 and under
df_75k = df
# df_75k = df_75k[df_75k['price'] <= 75000]
# df_75k = df_75k[df_75k['model_year'] >= 1980]
#df_75k = df_75k[df_75k['odometer'] <= 400000]
# Dropping 'other' vehicle type
df_75k = df_75k[df_75k['type'] != 'other']

st.write("Initial review of the dataset has discovered several outliers for vehicle listings priced above $75,000, model years older than 1980, and odometer readings over 400k miles.")
st.write("These findings are consistent throughout different vehicle types and makes, allowing the analysis to safely exclude these outliers.")

show_expensive_cars = st.checkbox("Include vehicles above $75,000")
if show_expensive_cars:
    df_75k = df_75k
else:
    df_75k = df_75k[df_75k['price'] <= 75000]

show_old_cars = st.checkbox("Include vehicles older than 1980")
if show_old_cars:
    df_75k = df_75k
else:
    df_75k = df_75k[df_75k['model_year'] >= 1980]

show_high_miles = st.checkbox("Include vehicles with more than 400,000 miles")
if show_high_miles:
    df_75k = df_75k
else:
    df_75k = df_75k[df_75k['odometer'] <= 400000]

# Visualizing the relationship between miles, price and model year
vehicles_filtered_price_v_miles_scat = px.scatter(
    df_75k,
    x='odometer',
    y='price',
    labels={'odometer': "Miles", 'price': "Price ($)"},
    title='Vehicle Price vs Miles'
)
st.plotly_chart(vehicles_filtered_price_v_miles_scat)
st.write("Miles have a negative correlation with price, indicating that as the odometer reading increases, the price tends to decrease.")

vehicles_75k_price_v_year = px.scatter(
    df_75k,
    x='model_year',
    y='price',
    labels={'model_year': "Model Year", 'price': "Price ($)"},
    title='Vehicle Price vs Model Year'
)
st.plotly_chart(vehicles_75k_price_v_year)
st.write("Model year has a positive correlation with price, indicating that newer vehicles tend to be priced higher than older vehicles.")

# Showing the distribution of vehicle prices for vehicles $75k and under
vehicle_prices_hist = px.histogram(
    df_75k,
    x='price',
    nbins=40,
    labels={'price': "Price ($)"},
    title='Distribution of Vehicle Prices ($75k and under)'
).update_yaxes(title_text="Listings")
st.plotly_chart(vehicle_prices_hist)

# Grouping vehicles $75k and under by type and calculating the mean price, odometer reading, and days listed
vehicles_by_type_75k = df_75k.groupby('type', observed=True).agg(
    count=('type', 'size'),
    avg_price=('price', 'mean'),
    avg_odometer=('odometer', 'mean'),
    percent_of_4wd=('is_4wd', lambda x: (x > 0).mean() * 75),
    avg_days_listed=('days_listed', 'mean'),
).reset_index()

# Visualizing the number of vehicle listings by type
vehicle_by_type_75k_bar = px.bar(
    vehicles_by_type_75k,
    x='type',
    y='count',
    labels={'type': "Vehicle Type", 'count': "Listings"},
    title='Vehicle Listings by Type ($75k and under)'
)
st.plotly_chart(vehicle_by_type_75k_bar)

top4_most_listed_type_75k = df_75k['type'].value_counts().head(4)
st.write("Top 4 most listed vehicle types ($75k and under):")
top4_listed_type_df = top4_most_listed_type_75k.to_frame() \
    .reset_index() \
    .rename(columns={'type': 'Vehicle Type', 'count': 'Listings'}) \
    .to_html(index=False)
st.write(top4_listed_type_df, unsafe_allow_html=True)

top4_least_listed_type_75k = df_75k['type'].value_counts()
top4_least_listed_type_75k = top4_least_listed_type_75k[top4_least_listed_type_75k.index != 'other']
top4_least_listed_type_75k = top4_least_listed_type_75k.tail(4).sort_values(ascending=True)
st.write("Top 4 least listed vehicle types ($75k and under):")
bott4_listed_type = top4_least_listed_type_75k.to_frame() \
    .reset_index() \
    .rename(columns={'type': 'Vehicle Type', 'count': 'Listings'}) \
    .to_html(index=False)
st.write(bott4_listed_type, unsafe_allow_html=True)

vehicle_prices_by_type_box = px.box(
    df_75k,
    x='type',
    y='price',
    labels={'type': "Vehicle Type", 'price': "Price ($)"},
    title='Vehicle Prices by Type ($75k and under)')
st.plotly_chart(vehicle_prices_by_type_box)

top4_expensive_type_75k = vehicles_by_type_75k.nlargest(4, 'avg_price')
top4_expensive_type_75k['avg_price'] = top4_expensive_type_75k['avg_price'].round(1)
st.write("Top 4 most expensive vehicle types by averge price ($75k and under):")
top4_expensive_type_75k_df = top4_expensive_type_75k[['type', 'avg_price']] \
    .reset_index(drop=True) \
    .rename(columns={'type': 'Vehicle Type', 'avg_price': 'Average Price ($)'}) \
    .to_html(index=False)
st.write(top4_expensive_type_75k_df, unsafe_allow_html=True)

top4_least_expensive_type_75k = vehicles_by_type_75k.nsmallest(4, 'avg_price')
top4_least_expensive_type_75k['avg_price'] = top4_least_expensive_type_75k['avg_price'].round(1)
st.write("Top 4 least expensive vehicle types by average price ($75k and under):")
top4_least_expensive_type_75k_df = top4_least_expensive_type_75k[['type', 'avg_price']] \
    .reset_index(drop=True) \
    .rename(columns={'type': 'Vehicle Type', 'avg_price': 'Average Price ($)'}) \
    .to_html(index=False)
st.write(top4_least_expensive_type_75k_df, unsafe_allow_html=True)

# Grouping vehicles $75k and under by make and calculating the mean price, odometer reading, and days listed
vehicles_by_make_75k = df_75k.groupby('make', observed=True).agg(
    count=('make', 'size'),
    avg_price=('price', 'mean'),
    avg_odometer=('odometer', 'mean'),
    percent_of_4wd=('is_4wd', lambda x: (x > 0).mean() * 75),
    avg_days_listed=('days_listed', 'mean'),
).reset_index()

# Visualizing the number of vehicle listings by make
vehicle_by_make_75k_bar = px.bar(
    vehicles_by_make_75k,
    x='make',
    y='count',
    labels={'make': "Make", 'count': "Listings"},
    title='Vehicle Listings by Make ($75k and under)'
)
st.plotly_chart(vehicle_by_make_75k_bar)

top4_most_listed_make_75k = df_75k['make'].value_counts().head(4)
st.write("Top 4 most listed vehicle makes ($75k and under):")
top4_listed_make_df = top4_most_listed_make_75k.to_frame() \
    .reset_index() \
    .rename(columns={'make': 'Make', 'count': 'Listings'}) \
    .to_html(index=False)
st.write(top4_listed_make_df, unsafe_allow_html=True)

top4_least_listed_make_75k = df_75k['make'].value_counts()
top4_least_listed_make_75k = top4_least_listed_make_75k[top4_least_listed_make_75k.index != 'other']
top4_least_listed_make_75k = top4_least_listed_make_75k.tail(4).sort_values(ascending=True)
st.write("Top 4 least listed vehicle makes ($75k and under):")
bott4_listed_make = top4_least_listed_make_75k.to_frame() \
    .reset_index() \
    .rename(columns={'make': 'Make', 'count': 'Listings'}) \
    .to_html(index=False)
st.write(bott4_listed_make, unsafe_allow_html=True)

vehicle_prices_by_make_box = px.box(
    df_75k,
    x='make',
    y='price',
    labels={'make': "Make", 'price': "Price ($)"},
    title='Vehicle Prices by Make ($75k and under)')
st.plotly_chart(vehicle_prices_by_make_box)

top4_expensive_make_75k = vehicles_by_make_75k.nlargest(4, 'avg_price')
top4_expensive_make_75k['avg_price'] = top4_expensive_make_75k['avg_price'].round(1)
st.write("Top 4 most expensive vehicle makes by average price ($75k and under):")
top4_expensive_make_75k_df = top4_expensive_make_75k[['make', 'avg_price']] \
    .reset_index(drop=True) \
    .rename(columns={'make': 'Make', 'avg_price': 'Average Price ($)'}) \
    .to_html(index=False)
st.write(top4_expensive_make_75k_df, unsafe_allow_html=True)

top4_least_expensive_make_75k = vehicles_by_make_75k.nsmallest(4, 'avg_price')
top4_least_expensive_make_75k['avg_price'] = top4_least_expensive_make_75k['avg_price'].round(1)
st.write("Top 4 least expensive vehicle makes by average price ($75k and under):")
top4_least_expensive_make_75k_df = top4_least_expensive_make_75k[['make', 'avg_price']] \
    .reset_index(drop=True) \
    .rename(columns={'make': 'Make', 'avg_price': 'Average Price ($)'}) \
    .to_html(index=False)
st.write(top4_least_expensive_make_75k_df, unsafe_allow_html=True)

# Grouping vehicles further by make and type
vehicles_by_maketype_75k = df_75k.groupby(['make', 'type'], observed=True).agg(
    count=('make', 'size'),
    avg_price=('price', 'mean'),
    avg_odometer=('odometer', 'mean'),
    percent_of_4wd=('is_4wd', lambda x: (x > 0).mean() * 75),
    avg_days_listed=('days_listed', 'mean')
).reset_index()
vehicles_by_maketype_75k[['avg_price', 'avg_odometer', 'percent_of_4wd', 'avg_days_listed']] = vehicles_by_maketype_75k[['avg_price', 'avg_odometer', 'percent_of_4wd', 'avg_days_listed']].round(1)

# Visualizing the number of vehicle listings by make and type
vehicles_by_maketype_75k['type'] = vehicles_by_maketype_75k['type'].cat.remove_unused_categories()
vehicles_by_make_type = px.bar(
    vehicles_by_maketype_75k,
    x='make',
    y='count',
    color='type',
    labels={'make': "Vehicle Make", 'count': "Listings"},
    title='Vehicle Listings by Make and Type ($75k and under)'
)
st.plotly_chart(vehicles_by_make_type)