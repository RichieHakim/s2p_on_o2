import paramiko
import time

class ssh_interface():
    """
    Interface to ssh to a remote server.
    Mostly a wrapper for paramiko.SSHClient.
    Tested on O2 cluster at Harvard.
    RH 2022
    """
    def __init__(
        self,
        nbytes_toReceive=4096,
        recv_timeout=1,
        verbose=True,
    ):
        """
        Args:
            nbytes_toReceive (int):
                Number of bytes to receive at a time.
                Caps the maximum message it can receive.
            recv_timeout (int):
                Timeout for receiving data.
            verbose (bool):
                Whether or not to print progress
        """
        
        self.nbytes = nbytes_toReceive
        self.recv_timeout = recv_timeout
        self.verbose=verbose
        
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    def connect(
        self,
        hostname='transfer.rc.hms.harvard.edu',
        username='rh183',
        password='',
        port=22
    ):
        """
        Connect to the remote server.
        Args:
            hostname (str):
                Hostname of the remote server.
            username (str):
                Username to log in with.
            password (str):
                Password to log in with.
                Is not stored.
            port (int):
                Port to connect to.
                sftp is always port 22.
        """
        self.client.connect(hostname=hostname, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        self.ssh = self.client.invoke_shell()

    def send(self, cmd='ls', append_enter=True):
        """
        Send a command to the remote server.
        Args:
            cmd (str):
                Command to send.
            append_enter (bool):
                Whether or not to append an enter
                 (backslash n) to the command.
                This is usually necessary to send.
        """
        if append_enter:
            cmd += '\n'
        self.ssh.send(cmd)
    
    def receive(self, timeout=None, verbose=None):
        """
        Receive data from the remote server.
        Args:
            timeout (int):
                Timeout for receiving data.
                If None, will use self.recv_timeout.
            verbose (bool):
                Whether or not to print progress.
        """
        if timeout is None:
            timeout = self.recv_timeout
        self.ssh.settimeout(timeout)
        
        out = self.ssh.recv(self.nbytes).decode('utf-8')
        if verbose is None:
            verbose=self.verbose
        if verbose:
            print(out)
        return out
    
    def send_receive(
        self, 
        cmd='ls', 
        append_enter=True,
        post_send_wait_t=0.1, 
        timeout=None, 
        verbose=None,
    ):
        """
        Send a command to the remote server,
         and receive the response.
        Args:
            cmd (str):
                Command to send.
            append_enter (bool):
                Whether or not to append an enter
                 (backslash n) to the command.
                This is usually necessary to send.
            post_send_wait_t (float):
                Time to wait after sending the command.
            timeout (int):
                Timeout for receiving data.
                If None, will use self.recv_timeout.
            verbose (bool):
                Whether or not to print progress.
        """
        self.send(cmd=cmd, append_enter=append_enter)
        time.sleep(post_send_wait_t)
        out = self.receive(timeout=timeout, verbose=verbose)   
        return out 
    
    def expect(
        self,
        str_success='(base) [rh183',
        partial_match=True,
        recv_timeout=0.3,
        total_timeout=60,
        verbose=None,
    ):
        """
        Wait for a string to appear in the output.
        Args:
            str_success (str):
                String to wait for.
            partial_match (bool):
                Whether or not to allow a partial match.
            recv_timeout (float):
                Timeout for receiving data per 
                 check iteration.
            total_timeout (float):
                Total time to wait for the string.
            verbose (bool):
                Whether or not to print progress.
                0/False: no printing
                1/True: will print recv outputs.
                2: will print expect progress.
                None: will default to self.verbose (1 or 2).
        """
        t_start = time.time()
        
        if recv_timeout is None:
            recv_timeout = self.recv_timeout
        if verbose is None:
            verbose = self.verbose
            
        success = False
        out=''
        while success is False:
            if verbose==2:
                print(f'=== expecting, t={time.time() - t_start} ===')
            
            try:
                out = self.receive(timeout=recv_timeout, verbose=verbose>0)
            except:
                if verbose==2:
                    print("expect: nothing received")
                    
            if partial_match:
                if str_success in out:
                    success = True
            else:
                if str_success == out:
                    success = True
            
            if time.time() - t_start > total_timeout:
                break
        
        if verbose==2:
            if success:
                print(f'expect succeeded')
            else:
                print(f'expect failed')
                
        return out, success
        
    def close(self):
        self.ssh.close()
        
    def __del__(self):
        self.ssh.close()

            
    def o2_connect(
        self,
        hostname='transfer.rc.hms.harvard.edu',
        username='rh183',
        password='',
        passcode_method=1,
        verbose=1,
    ):
        """
        Connect to the O2 cluster.
        Helper function with some hard-coded expectations.
        Args:
            hostname (str):
                Hostname of the remote server.
            username (str):
                Username to log in with.
            password (str):
                Password to log in with.
                Is not stored.
            passcode_method (int):
                Method to use for O2 passcode.
                1. Duo Push
                2. Phone call
                3. SMS passcodes
            verbose (int):
                0/False: no printing
                1/True: will print recv outputs.
                2: will print expect progress.
                None: will default to self.verbose (1 or 2).
        """
        self.connect(
            hostname=hostname,
            username=username,
            password=password,
            port=22
        )
        
        self.expect(
            str_success=f'Passcode or option (1-3)',
            partial_match=True,
            recv_timeout=0.3,
            total_timeout=60,
            verbose=verbose,
        )
        
        self.send(cmd=str(passcode_method))
        
        self.expect(
            str_success=f'[{username}@',
            partial_match=True,
            recv_timeout=0.3,
            total_timeout=60,
            verbose=verbose,
        )
        