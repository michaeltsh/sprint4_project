import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv('vehicles_us.csv')
# Fixing data
# Filling in missing values in 'model_year', 'odometer', and 'cylinders' columns with median values relative to vehicle types
df['model_year'] = df.groupby('type')['model_year'].transform(lambda x: x.fillna(x.median()))
df['odometer'] = df.groupby('type')['odometer'].transform(lambda x: x.fillna(x.median()))
df['cylinders'] = df.groupby('type')['cylinders'].transform(lambda x: x.fillna(x.median()))

# Convert multiple columns to int at once 
int_cols = ['model_year', 'odometer', 'price', 'days_listed', 'cylinders']
for col in int_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('int')

# Filling NaN in is_4wd'with 0 and changing to bool dtype
df['is_4wd'] = df['is_4wd'].fillna(0).astype("bool")

# Converting mltiple columns to category dtype and filling NaN values in 'paint_color' with 'unknown'
cat_cols = ['model', 'condition', 'fuel', 'transmission', 'type', 'paint_color']
for col in cat_cols:
    df[col] = df[col].astype('category')
df['paint_color'] = df['paint_color'].cat.add_categories(['unknown']).fillna('unknown')


# Converting 'date_posted' column to datetime dtype
df['date_posted'] = pd.to_datetime(df['date_posted'], errors='coerce')
# Droping rows with null 'model_year' or 'odometer' values
#df = df.dropna(subset=['model_year', 'odometer'])

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
st.write("Use the checkboxes below to include outliers in the analysis.")
# Creating a new DF with 'other' vehicle type removed,
# and only including vehicles priced up to $75,000, model year 1980 and newer and miles 400,000 and under
filtered_df = df.copy()
filtered_df = filtered_df[filtered_df['type'] != 'other']

# Create columns for a cleaner layout
col1, col2, col3 = st.columns(3)

with col1:
    if not st.checkbox("Include vehicles > $75,000", key='expensive'):
        filtered_df = filtered_df[filtered_df['price'] <= 75000]

with col2:
    if not st.checkbox("Include vehicles older than 1980", key='old'):
        filtered_df = filtered_df[filtered_df['model_year'] >= 1980]

with col3:
    if not st.checkbox("Include vehicles > 400k miles", key='high_miles'):
        filtered_df = filtered_df[filtered_df['odometer'] <= 400000]

st.write("Initial review of the dataset has discovered several outliers for vehicle listings priced above $75,000, model years older than 1980, and odometer readings over 400k miles.")
st.write("These findings are consistent throughout different vehicle types and makes, allowing the analysis to safely exclude these outliers.")

# Old Code -- IGNORE
#show_expensive_cars = st.checkbox("Include vehicles above $75,000")
#if show_expensive_cars:
    #filtered_df = filtered_df
#else:
    #filtered_df = filtered_df[filtered_df['price'] <= 75000]

#show_old_cars = st.checkbox("Include vehicles older than 1980")
#if show_old_cars:
    #filtered_df = filtered_df
#else:
    #filtered_df = filtered_df[filtered_df['model_year'] >= 1980]

#show_high_miles = st.checkbox("Include vehicles with more than 400,000 miles")
#if show_high_miles:
    #filtered_df = filtered_df
#else:
    #filtered_df = filtered_df[filtered_df['odometer'] <= 400000]

# Visualizing the relationship between miles, price and model year
vehicles_filtered_price_v_miles_scat = px.scatter(
    filtered_df,
    x='odometer',
    y='price',
    labels={'odometer': "Miles", 'price': "Price ($)"},
    title='Vehicle Price vs Miles'
)
st.plotly_chart(vehicles_filtered_price_v_miles_scat)
st.write("Miles have a negative correlation with price, indicating that as the odometer reading increases, the price tends to decrease.")

vehicles_75k_price_v_year = px.scatter(
    filtered_df,
    x='model_year',
    y='price',
    labels={'model_year': "Model Year", 'price': "Price ($)"},
    title='Vehicle Price vs Model Year'
)
st.plotly_chart(vehicles_75k_price_v_year)
st.write("Model year has a positive correlation with price, indicating that newer vehicles tend to be priced higher than older vehicles.")

# Showing the distribution of vehicle prices for vehicles $75k and under
vehicle_prices_hist = px.histogram(
    filtered_df,
    x='price',
    nbins=40,
    labels={'price': "Price ($)"},
    title='Distribution of Vehicle Prices ($75k and under)'
).update_yaxes(title_text="Listings")
st.plotly_chart(vehicle_prices_hist)

# Grouping vehicles $75k and under by type and calculating the mean price, odometer reading, and days listed
vehicles_by_type_75k = filtered_df.groupby('type', observed=True).agg(
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

top4_most_listed_type_75k = filtered_df['type'].value_counts().head(4)
st.write("Top 4 most listed vehicle types ($75k and under):")
top4_listed_type_df = top4_most_listed_type_75k.to_frame() \
    .reset_index() \
    .rename(columns={'type': 'Vehicle Type', 'count': 'Listings'}) \
    .to_html(index=False)
st.write(top4_listed_type_df, unsafe_allow_html=True)

top4_least_listed_type_75k = filtered_df['type'].value_counts()
top4_least_listed_type_75k = top4_least_listed_type_75k[top4_least_listed_type_75k.index != 'other']
top4_least_listed_type_75k = top4_least_listed_type_75k.tail(4).sort_values(ascending=True)
st.write("Top 4 least listed vehicle types ($75k and under):")
bott4_listed_type = top4_least_listed_type_75k.to_frame() \
    .reset_index() \
    .rename(columns={'type': 'Vehicle Type', 'count': 'Listings'}) \
    .to_html(index=False)
st.write(bott4_listed_type, unsafe_allow_html=True)

vehicle_prices_by_type_box = px.box(
    filtered_df,
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
vehicles_by_make_75k = filtered_df.groupby('make', observed=True).agg(
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

top4_most_listed_make_75k = filtered_df['make'].value_counts().head(4)
st.write("Top 4 most listed vehicle makes ($75k and under):")
top4_listed_make_df = top4_most_listed_make_75k.to_frame() \
    .reset_index() \
    .rename(columns={'make': 'Make', 'count': 'Listings'}) \
    .to_html(index=False)
st.write(top4_listed_make_df, unsafe_allow_html=True)

top4_least_listed_make_75k = filtered_df['make'].value_counts()
top4_least_listed_make_75k = top4_least_listed_make_75k[top4_least_listed_make_75k.index != 'other']
top4_least_listed_make_75k = top4_least_listed_make_75k.tail(4).sort_values(ascending=True)
st.write("Top 4 least listed vehicle makes ($75k and under):")
bott4_listed_make = top4_least_listed_make_75k.to_frame() \
    .reset_index() \
    .rename(columns={'make': 'Make', 'count': 'Listings'}) \
    .to_html(index=False)
st.write(bott4_listed_make, unsafe_allow_html=True)

vehicle_prices_by_make_box = px.box(
    filtered_df,
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
vehicles_by_maketype_75k = filtered_df.groupby(['make', 'type'], observed=True).agg(
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

# Grouping by 'type' and 'is_4wd', then count
vehicles_4wd_type_split = filtered_df.groupby(['type', 'is_4wd'], observed=True).size().reset_index(name='count')

# Map True/False to readable labels
vehicles_4wd_type_split['4WD'] = vehicles_4wd_type_split['is_4wd'].map({True: '4WD', False: 'Not 4WD'})

vehicle_types_4wd_split_bar = px.bar(
    vehicles_4wd_type_split,
    x='type',
    y='count',
    color='4WD',  # use the new column for legend
    barmode='stack',
    labels={'type': "Vehicle Type", 'count': "Listings", '4WD': ""},
    title='Distribution of 4WD Vehicles by Type ($75k and under)'
)
st.plotly_chart(vehicle_types_4wd_split_bar)

# Grouping by 'make' and 'is_4wd', then count
vehicles_4wd_make_split = filtered_df.groupby(['make', 'is_4wd'], observed=True).size().reset_index(name='count')

# Map True/False to readable labels
vehicles_4wd_make_split['4WD'] = vehicles_4wd_make_split['is_4wd'].map({True: '4WD', False: 'Not 4WD'})

vehicle_makes_4wd_split_bar = px.bar(
    vehicles_4wd_make_split,
    x='make',
    y='count',
    color='4WD',  # use the new column for legend
    barmode='stack',
    labels={'make': "Vehicle Make", 'count': "Listings", '4WD': ""},
    title='Distribution of 4WD Vehicles by Make ($75k and under)'
)
st.plotly_chart(vehicle_makes_4wd_split_bar)

st.subheader("Exploratory Data Analysis Summary:")
st.write(
    "- The dataset contains vehicle listings with details including price, model year, make, model, etc.\n"
    "- Data cleaning involved filling missing values, converting data types, and removing outliers.\n"
    "- The outliers removed were vehicles priced over $75,000, older than year 1980 and odometer readings over 400,000 miles.\n"
    "- Relationship between vehicle attributes are as expected, where price and miles shows a negative correlation, while price and model year shows a positive correlation.\n"
    "- Majority of vehicles are automatic transmission, with gas fuel being the most common type.\n"
    "- The dataset of vehicles having AWD is split nearly 50/50, but the split of 4WD vehicles by type and make varies significantly.\n"
)