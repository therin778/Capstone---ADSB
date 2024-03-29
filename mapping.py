#mapping function for main
#last update 04/11/23

import folium
import random

show_trail = True  #Set to True to show trail
all_icons = False  #Set to True to show all icons, False to show first and last

def mapping(aircraft):


    print("inside mapping")
    test_lat =  37.066707287804554
    test_long = 13.802470331606658

    ohio_lat = 39.3292
    ohio_long = -82.1013

    map = folium.Map(location=[ohio_lat, ohio_long])

    print(len(aircraft)) 

    def popup_html(ICAO, tail, latitude, altitude, longitude, velocity, heading):
        return f"""
            <div>
                <svg height="80" width="150">
                    <text fill="black" font-size="12" font-family="Verdana" x="0" y="10">ICAO: {ICAO[2:]}</text>
                    <text fill="black" font-size="12" font-family="Verdana" x="0" y="21">Tail number: {tail.replace("_", "")}</text>
                    <text fill="black" font-size="12" font-family="Verdana" x="0" y="32">Latitude: {latitude:.5f}°</text>
                    <text fill="black" font-size="12" font-family="Verdana" x="0" y="43">Longitude: {longitude:.5f}°</text>
                    <text fill="black" font-size="12" font-family="Verdana" x="0" y="54">Altitude: {altitude:.0f} ft.</text>
                    <text fill="black" font-size="12" font-family="Verdana" x="0" y="65">Velocity: {velocity:.1f} kts</text>
                    <text fill="black" font-size="12" font-family="Verdana" x="0" y="76">Heading: {heading:.1f}°</text>
                </svg>
            </div>
        """

    for plane in aircraft:

        coord_pair = []
        map_finished = False

        plane_list = str(hex(int(plane.ID,2)))
        ICAO = str(hex(int(plane.ID,2)))
        tail = plane.tail
        lat_list = plane.lat
        long_list =plane.long
        alt_list = plane.alt
        heading_list = plane.heading
        vel_list = plane.vel
        print("plane_list: ", plane_list)

        # this is a hack to make the program stop crashing, i will fix this properly later
        loop_len = 0
        if len(lat_list) >= len(vel_list):
            loop_len = len(vel_list)
        else:
            loop_len = len(lat_list)
        

        for i in range(loop_len):

            icon_path = r"./Icons/Plane Icon" #Set to icon path

            if heading_list[len(heading_list)-1] >= -9 and heading_list[len(heading_list)-1] <= 9: icon_path += " 0.png"

            if heading_list[len(heading_list)-1] > 9 and heading_list[len(heading_list)-1] <= 27: icon_path += " 18.png"
            if heading_list[len(heading_list)-1] > 27 and heading_list[len(heading_list)-1] <= 45: icon_path += " 36.png"
            if heading_list[len(heading_list)-1] > 45 and heading_list[len(heading_list)-1] <= 63: icon_path += " 54.png"
            if heading_list[len(heading_list)-1] > 63 and heading_list[len(heading_list)-1] <= 81: icon_path += " 72.png"
            if heading_list[len(heading_list)-1] > 81 and heading_list[len(heading_list)-1] <= 99: icon_path += " 90.png"
            if heading_list[len(heading_list)-1] > 99 and heading_list[len(heading_list)-1] <= 117: icon_path += " 108.png"
            if heading_list[len(heading_list)-1] > 117 and heading_list[len(heading_list)-1] <= 135: icon_path += " 126.png"
            if heading_list[len(heading_list)-1] > 135 and heading_list[len(heading_list)-1] <= 153: icon_path += " 144.png"
            if heading_list[len(heading_list)-1] > 153 and heading_list[len(heading_list)-1] <= 171: icon_path += " 162.png"

            if heading_list[len(heading_list)-1] < -9 and heading_list[len(heading_list)-1] >= -27: icon_path += " -18.png"
            if heading_list[len(heading_list)-1] < -27 and heading_list[len(heading_list)-1] >= -45: icon_path += " -36.png"
            if heading_list[len(heading_list)-1] < -45 and heading_list[len(heading_list)-1] >= -63: icon_path += " -54.png"
            if heading_list[len(heading_list)-1] < -63 and heading_list[len(heading_list)-1] >= -81: icon_path += " -72.png"
            if heading_list[len(heading_list)-1] < -81 and heading_list[len(heading_list)-1] >= -99: icon_path += " -90.png"
            if heading_list[len(heading_list)-1] < -99 and heading_list[len(heading_list)-1] >= -117: icon_path += " -108.png"
            if heading_list[len(heading_list)-1] < -117 and heading_list[len(heading_list)-1] >= -135: icon_path += " -126.png"
            if heading_list[len(heading_list)-1] < -135 and heading_list[len(heading_list)-1] >= -153: icon_path += " -144.png"
            if heading_list[len(heading_list)-1] < -153 and heading_list[len(heading_list)-1] >= -171: icon_path += " -162.png"

            if heading_list[len(heading_list)-1] > 171 or heading_list[len(heading_list)-1] < -171: icon_path += " 180.png"

            if not heading_list: icon_path += " 0.png"

            message = plane_list

            html=f"""
                <div>
                    <button onclick="show_popup(this)"><b>{plane_list}</b></button>
                </div>
            """
            if all_icons == True:
                folium.Marker(
                    [float(lat_list[i]), float(long_list[i])], 
                    icon=folium.CustomIcon(icon_image=icon_path, icon_size=(25, 25)),
                    popup=folium.Popup(popup_html(ICAO, tail, lat_list[i], alt_list[i], long_list[i], vel_list[i], heading_list[i]), max_width=200)
                ).add_to(map)
        
            if all_icons == False:
                if i == 0 or i == len(lat_list) - 1:
                    folium.Marker(
                    [float(lat_list[i]), float(long_list[i])], 
                    icon=folium.CustomIcon(icon_image=icon_path, icon_size=(25, 25)),
                    popup=folium.Popup(popup_html(ICAO, tail, lat_list[i], alt_list[i], long_list[i], vel_list[i], heading_list[i]), max_width=200)
                ).add_to(map)

            coord_pair.append([float(lat_list[i]), float(long_list[i])])
            map_finished = True

        if(show_trail):
            if(map_finished):
                color = '#' + str(hex(random.randint(1,16777216)))[2:] # looks weird, but it just generates a random hex color code
                folium.PolyLine(locations = coord_pair,
                    color=color,
                    weight=2,
                    opacity=1,
                    dash_array=[10, 5]).add_to(map)

    map.save("disp_map.html")