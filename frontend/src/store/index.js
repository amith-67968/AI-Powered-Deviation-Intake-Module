import { configureStore } from '@reduxjs/toolkit';
import deviationReducer from '../features/deviations/deviationSlice';
export const store = configureStore({ reducer: { deviation: deviationReducer } });
