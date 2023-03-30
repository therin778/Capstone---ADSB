#mapping function for main
#last update 03/30/23

import folium

show_trail = True  #Set to True to show trail

def mapping(aircraft):


    print("inside mapping")
    test_lat =  37.066707287804554
    test_long = 13.802470331606658

    ohio_lat = 39.3292
    ohio_long = -82.1013

    map = folium.Map(location=[test_lat, test_long])

    print(len(aircraft)) 

    def popup_html(message, latitude, altitude, longitude, velocity):
        return f"""
            <div>
                <svg height="300" width="300">
                    <rect x="10" y="10" width="200" height="160"
                    style="fill:white;stroke:black;stroke-width:2;opacity:0.5" />
                    <text fill="black" font-size="12" font-family="Verdana" x="15" y="30">ICAO: {message}</text>
                    <text fill="black" font-size="12" font-family="Verdana" x="15" y="40">Latitude: {latitude:.4f}</text>
                    <text fill="black" font-size="12" font-family="Verdana" x="15" y="50">Altitude: {altitude:.4f}</text>
                    <text fill="black" font-size="12" font-family="Verdana" x="15" y="60">Longitude: {longitude:.4f}</text>
                    <text fill="black" font-size="12" font-family="Verdana" x="15" y="70">Velocity: {velocity:.4f}</text>
                </svg>
            </div>
        """

    for plane in aircraft:

        coord_pair = []
        map_finished = False

        plane_list = str(hex(int(plane.ID,2)))
        lat_list = plane.lat
        long_list =plane.long
        alt_list = plane.alt
        heading_list = plane.heading
        vel_list = plane.vel
        print("plane_list: ", plane_list)


        for i in range(len(lat_list)):

            message = plane_list

            html=f"""
                <div>
                    <button onclick="show_popup(this)"><b>{plane_list}</b></button>
                </div>
            """

            folium.Marker(
                [float(lat_list[i]), float(long_list[i])], 
                icon=folium.DivIcon(html=html),
                popup=folium.Popup(popup_html(message, lat_list[i], alt_list[i], long_list[i], vel_list[i]), max_width=200)
            ).add_to(map)
        
            coord_pair.append([float(lat_list[i]), float(long_list[i])])
            map_finished = True

        if(show_trail):
            if(map_finished):
                folium.PolyLine(locations = coord_pair,
                    color='blue',
                    weight=2,
                    opacity=1,
                    dash_array=[10, 5]).add_to(map)

    map.save("disp_map.html")