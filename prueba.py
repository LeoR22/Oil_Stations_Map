if c3.button('SHOW MAP'):
    # Your existing code...

    gdf_stores_results2 = gdf_stores_results[gdf_stores_results['Producto']==choose_products]
    gdf_stores_results2 = gdf_stores_results2.reset_index()
    gdf_stores_results2 = gdf_stores_results2.drop(columns = 'index')
    icono = "usd"

    m = folium.Map([geo_source[0],geo_source[1]], zoom_start=15)

    # Circle
    folium.Circle(
        radius=int(rad)*1000,
        location=[geo_source[0],geo_source[1]],
        color='green',
        fill='red').add_to(m)

    # Centroid
    folium.Marker(location=[geo_source[0],geo_source[1]],
                        icon=folium.Icon(color='black', icon_color='white',
                        icon="home", prefix='glyphicon')
                        ,popup = "<b>CENTROID</b>").add_to(m)

    marker_rest(gdf_stores_results2,m,unit,choose_products,icono)

    # call to render Folium map in Streamlit
    folium_static(m)

    def handle_click(lat, lon):
        clicked_location = (lat, lon)
        st.write(f"Clicked Location: {clicked_location}")

        # Calculate the route from the central location to the clicked location
        central_location_coords = (geo_source[0], geo_source[1])  # Use the central location coordinates
        route = calculate_route(central_location_coords, clicked_location)

        # Plot the route on the map
        folium.PolyLine(route, color="blue", weight=2.5, opacity=1).add_to(m)

    # Add click event handler to the map
    m.add_child(folium.ClickForMarker(popup=None, callback=handle_click))
