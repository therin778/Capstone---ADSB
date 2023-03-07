#mapping function for main
#last update 03/06/23

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
                    <svg height="300" width="200">
                        <rect x="10" y="10" width="180" height="120"
                        style="fill:white;stroke:black;stroke-width:2;opacity:0.5" />
                        <text fill="black" font-size="12" font-family="Verdana" x="15" y="30">ICAO: {message}</text>
                        <text fill="black" font-size="12" font-family="Verdana" x="15" y="50">Altitude: {alt_list[i]}</text>
                        <text fill="black" font-size="12" font-family="Verdana" x="15" y="70">Longitude: {long_list}</text>
                        <text fill="black" font-size="12" font-family="Verdana" x="15" y="90">Velocity: {vel_list[i]}</text>
                    </svg>
                </div>
            """
            #folium.CircleMarker(
            #    location   = [float(lat_list[i]), float(long_list[i])],
            #    radius     = 50,
            #    popup      = "Athens",
            #    color      = "#3186cc",
            #    fill       = True,
            #    fill_color = "#3186cc",
            #).add_to(map)

            folium.Marker(
                [float(lat_list[i]), float(long_list[i])], icon=folium.DivIcon(html=html),
                popup = folium.Popup(html=html, auto_close=False)
            ).add_to(map)
        
            folium.Marker(
                [float(lat_list[i]), float(long_list[i])], popup="<i>Athens</i>"
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
