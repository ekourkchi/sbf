FROM ekourkchi/sbf_base:v1.0

# Copy everything from /sbf/packages/src to /src
COPY packages/src /src
COPY scripts/inDocker_install.sh /scripts/
RUN bash /scripts/inDocker_install.sh all

# Remove /src after the installation is done
RUN rm -rf /src

COPY scripts/setup_env.sh /scripts/
RUN chmod +x /scripts/setup_env.sh
RUN echo 'source /scripts/setup_env.sh' >> /root/.bashrc

# # Create a working directory
WORKDIR /notebooks

# # Expose port for Jupyter Notebook
EXPOSE 8888

# # Set the default command to start Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]

