import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import * as React from 'react';
import { Text, View, StyleSheet } from 'react-native';

import TabBarIcon from '../components/TabBarIcon';
import HomeScreen from '../screens/HomeScreen';
import LinksScreen from '../screens/LinksScreen';

const BottomTab = createBottomTabNavigator();
const INITIAL_ROUTE_NAME = 'Home';

export default function BottomTabNavigator({ navigation, route }) {
  // Set the header title on the parent stack navigator depending on the
  // currently active tab. Learn more in the documentation:
  // https://reactnavigation.org/docs/en/screen-options-resolution.html
  navigation.setOptions({
    headerTitle: getHeaderTitle(route),
    headerRight: () => {},
    headerTitleAlign: 'center',
    headerStyle: {
      backgroundColor: '#00756A',
      height: 120
    },
    headerTintColor: '#f2f2f2'
  });

  return (
    <BottomTab.Navigator initialRouteName={INITIAL_ROUTE_NAME}>
      <BottomTab.Screen
        name="Python"
        component={HomeScreen}
        options={{
          title: 'Python',
          tabBarIcon: ({ focused }) => <TabBarIcon focused={focused} name="ios-appstore" />,
        }}
      />
      <BottomTab.Screen
        name="JavaScript"
        component={LinksScreen}
        options={{
          title: 'JavaScript',
          tabBarIcon: ({ focused }) => <TabBarIcon focused={focused} name="ios-bulb" />,
        }}
      />
    </BottomTab.Navigator>
  );
}

const getHeaderTitle = (route) => {
  return (
    <View>
      <View>
        <Text  style={styles.title}>Package Picker</Text>
      </View>
      <View>
        <Text  style={styles.subTitle}>Better packages, faster</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  title: {
    textAlignVertical: "center",
    textAlign: "center",
    fontSize: 50
  },
  subTitle: {
    textAlignVertical: "center",
    textAlign: "center",
    fontSize: 20
  },
});
