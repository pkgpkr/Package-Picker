import * as Linking from 'expo-linking';

export default {
  prefixes: [Linking.makeUrl('/')],
  config: {
    Home: {
      path: 'home',
      screens: {
        Python: 'python',
        JavaScript: 'javascript',
      },
    },
  },
};
