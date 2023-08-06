import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { ApplicationProvider, IconRegistry } from "@ui-kitten/components";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Home } from "./src/screens/Home.js";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { Login } from "./src/screens/Login.js";
import * as eva from "@eva-design/eva";
import { EvaIconsPack } from "@ui-kitten/eva-icons";
import * as RootNavigation from "./src/components/RootNavigation";

const Tab1 = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = { authenticated: false };
  }

  render() {
    return (
      <NavigationContainer ref={RootNavigation.navigationRef}>
        <ApplicationProvider {...eva} theme={{ ...eva.dark }}>
          <IconRegistry icons={EvaIconsPack} />
          <SafeAreaProvider>
            {this.state.authenticated ? (
              <Tab1.Navigator>
                <Tab1.Screen name={"Home"}>{() => <Home />}</Tab1.Screen>
              </Tab1.Navigator>
            ) : (
              <Stack.Navigator>
                <Stack.Screen name={"Login"}>{() => <Login />}</Stack.Screen>
              </Stack.Navigator>
            )}
          </SafeAreaProvider>
        </ApplicationProvider>
      </NavigationContainer>
    );
  }
}
