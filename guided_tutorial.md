# **Guided Tutorial for Building Monitors**

## **1. Designing the Monitor**

For the hazard: **"Decreased image quality leading to inaccurate diagnostic results,"** we will design a monitor with the following components:

1. **Data Collection**  
   - Track the number of images that pass and fail the image quality check and the camera type.

2. **Visualization**  
   - Plot the rate of low-quality images for differnt cameras over time.

3. **Alerts**  
   - Notify users when the low-quality image rate exceeds a preset threshold.

## **2. Implementing Data Collection**

1. Open the file: **`backend/aeye/consumers.py`**.  
2. Review lines **18 to 58** (you may explore other parts if needed, but it's not required).  
3. In **Step 2 (lines 33-50)**, note that:  
   - If an image **fails** the quality check, processing stops (this case is already implemented).  
   - If an image **passes**, it continues to the next step.  

### **Your Task:**

Modify the code to **send a metric to Grafana** for **each successful image verification**, just as we do for failed cases.

## **3. Implementing Visualization & Alerts**

1. **Sign in to Grafana**:  
   - Go to [Grafana Login](https://grafana.com/auth/sign-in/)  
   - Use credentials:  
     - **Username:** `safeguard4mlrisk`  
     - **Password:** `safeguard4mlrisk`  

2. **Access the Dashboard**:  
   - Visit: [Dashboard](https://hyn0027.grafana.net/)  

We will guide you through setting up visualizations and alerts in Grafana.
