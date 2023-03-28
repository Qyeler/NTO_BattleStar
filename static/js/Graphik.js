fetch("username.txt")
  .then(response => response.text())
  .then(data => {
    var lines = data.split("\n");
    var values = lines.map(line => {
      var parts = line.split(",");
      return {
        day: parseInt(parts[0]),
        hour: parseInt(parts[1]),
        minute: parseInt(parts[2]),
        second: parseInt(parts[3]),
        value: parseFloat(parts[4])
      };
    });
    console.log(values);
  });