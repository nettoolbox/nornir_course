import os
from nornir import InitNornir
from nornir.core.filter import F
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.networking import netmiko_send_command


def main():
    nr = InitNornir(config_file="config.yaml", core={"num_workers": 15})
    ios_filt = F(groups__contains="ios")
    nr = nr.filter(ios_filt)

    # Set one of the devices to an invalid password
    nr.inventory.hosts["cisco3"].password = "bogus"
    my_results = nr.run(task=netmiko_send_command, command_string="show ip int brief")

    print("\n\n")
    print("Executing Task: cisco3 will fail:")
    print("-" * 40)
    print_result(my_results)
    print()
    print(f"Task failed hosts: {my_results.failed_hosts}")
    print(f"Global failed hosts: {nr.data.failed_hosts}")
    print()

    # Re-set password back to valid value
    nr.inventory.hosts["cisco3"].password = os.environ["NORNIR_PASSWORD"]

    # Nornir doesnt reset connection for failed hosts causing issues
    print(nr.inventory.hosts["cisco3"].connections)
    try:
        nr.inventory.hosts["cisco3"].close_connections()
    except ValueError:
        pass

    my_results = nr.run(
        task=netmiko_send_command,
        command_string="show ip int brief",
        on_good=False,
        on_failed=True,
    )

    print("\n\n")
    print("Executing Task: only on cisco3 - task should succeed:")
    print("-" * 40)
    print_result(my_results)
    print()
    print(f"Task failed hosts: {my_results.failed_hosts}")
    print(f"Global failed hosts: {nr.data.failed_hosts}")
    print("\n\n")
    print("Recovering failed_host")
    print("-" * 40)
    nr.data.recover_host("cisco3")
    print(f"Global failed hosts: {nr.data.failed_hosts}")
    print()


if __name__ == "__main__":
    main()
