directory = 'IndividualPeerInfoLog_24_hours_preliminary'
files = {'120.79.71.72.csv', '139.59.145.220.csv', '144.137.29.181.csv', '15.228.89.32.csv', '150.136.83.181.csv', '157.90.130.44.csv', '159.223.217.27.csv', '162.218.218.163.csv', '195.228.75.150.csv', '198.199.82.190.csv', '34.101.77.203.csv', '38.242.242.88.csv', '64.187.175.226.csv', '65.21.125.44.csv', '72.206.123.63.csv', '73.223.253.232.csv', '85.215.9.88.csv', '93.115.27.167.csv', '95.111.229.184.csv'}

font_size = 18
line_width = 2
use_pseudonyms = 1
onlyFocusOnNumPeers = 0 % Zero for all peers
legendPosition = 'EastOutside'
legendNumColumns = 1
legendFontSize = 8
colors = {'#747E7E', '#72F2EB', '#00CCBF', '#3F7C85', '#405952', '#9C9B7A', '#FFD393', '#FF974F', '#F54F29', '#FF7DD4'}
%figure('Position', [100 100 1500 600])

addresses = []

hold on
for i=1:length(files)
    filePath = strcat(directory, '/', files{i});
    data = readmatrix(filePath);

    name = strcat('Node ', num2str(i))
    fees = data(:, 11)
    sizes = data(:, 12)
    addresses{i} = name
    

    if i <= length(colors)
        plot(sizes, fees, '.', 'Color', colors{i})
    else
        plot(sizes, fees, '.')
    end
end

x=[162,10^6]
plot(x, x, '--', 'Color', 'black')
addresses{i+1} = 'y = x'
xlim([162, 10^6])
ylim([162, 10^6])

xlabel('Transaction Size (B)')
ylabel('Transaction Fee (satoshis)')

axis square;
grid on;
box on;
set(gca, 'FontSize', font_size);
set(gca, 'XMinorTick','on', 'XMinorGrid','off', 'YMinorTick','on', 'YMinorGrid','on');
set(gca, 'XScale', 'log')
set(gca, 'YScale', 'log')
%xtickangle(45)

legend(addresses, 'Location', legendPosition, 'NumColumns', legendNumColumns, 'FontSize', legendFontSize)